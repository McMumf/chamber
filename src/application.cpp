#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

#include <chrono>
#include <cmath>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <numeric>
#include <string>
#include <thread>
#include <vector>

#include "Adafruit_GFX.h"
#include "ArduiPi_OLED.h"
#include "ArduiPi_OLED_lib.h"
#include <bcm2835.h>
#include "./ds18b20/ds18b20.h"
#include "pigpio.h"

using namespace std::literals::chrono_literals;

// Instantiate the display.
ArduiPi_OLED display;

// Control cycle worker variables.
bool main_ready;
bool worker_ready;
std::mutex m;
std::condition_variable cv;
std::chrono::system_clock::time_point start_time;
std::chrono::duration<double> diff;

volatile sig_atomic_t stop;
double control_cycle = 0.500; // Seconds
int temp_target = 23;
std::vector<float> temps(8, 0);
unsigned int ModeGpio = 23;
unsigned int incInputGpio = 5;
unsigned int decInputGpio = 16;
unsigned int FanPWM = 18;
unsigned int PeltierPWM = 19;

// Interruption handler for CTRL-C quit.
void inthand(int signum) { stop = 1; }

/**
 * Temperature in Celsius measured with an
 *
 * @returns temperature in Celsius
 */
float get_temp(int channel = 0)
{

  readTemp()

      return temp;
}

// Convert temperature from Celsius to Fahrenheit.
/**
 * Convert temperature from Celsius to Fahrenheit.
 *
 * @param temp_C - temperature in Celsius
 * @returns the temperatire in Fahrenheit
 */
float celsius_to_fahrenheit(float temp_C) { return (temp_C * 9.0 / 5.0 + 32); }

/**
 * Display text passed to function on OLED.
 *
 * @param string - text to display
 * @returns 0 if success
 */
int display_text(const char *string)
{
  const char *text = string;

  display.clearDisplay();
  display.display();

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.print(text);
  display.display();

  return 0;
}

// Initialize OLED display.
int display_init(void)
{
  // Configure display model and pins.
  const int OLED_TYPE = 0;       // OLED_ADAFRUIT_SPI_128x32
  const int OLED_SPI_DC = 6;     // RPI GPIO 6 pin 31
  const int OLED_SPI_RESET = 26; // RPI GPIO 26 pin 37
  const int OLED_SPI_CS = 1;     // BCM2835_SPI_CS1

  if (!display.init(OLED_SPI_DC, OLED_SPI_RESET, OLED_SPI_CS, OLED_TYPE))
    exit(EXIT_FAILURE);
  display.begin();

  return 0;
}

// Enforce the control cycle time.
void dt_control()
{
  // Wait until main() sends data.
  std::unique_lock<std::mutex> lk(m);
  cv.wait(lk, []
          { return main_ready; });

  diff = std::chrono::system_clock::now() - start_time;

  // Wait until control cycle is up.
  while (diff.count() < control_cycle)
  {
    diff = std::chrono::system_clock::now() - start_time;
  }

  // Send data back to main().
  worker_ready = true;
  // Manual unlocking is done before notifying, to avoid waking up
  // the waiting thread only to block again (see notify_one for details).
  lk.unlock();
  cv.notify_one();
}

// Increase temperature setpoint.
void increase_setpoint(int gpio, int level, uint32_t tick)
{
  if (level == 0)
  { // Only increment on the falling edge.
    temp_target++;
    std::cout << "GPIO triggered: " << gpio << std::endl;
  }
}

// Decrease temperature setpoint.
void decrease_setpoint(int gpio, int level, uint32_t tick)
{
  if (level == 0)
  { // Only decrement on the falling edge.
    temp_target--;
    std::cout << "GPIO triggered: " << gpio << std::endl;
  }
}

int main(void)
{
  std::string mode;
  int chan = 0;
  int loop_count = 0;
  int flip_flop = 0;
  float sum, temp = 0;
  int duty_cycle_inner, duty_cycle_peltier_outer, samples;

  // Initialize display.
  display_init();

  // Initialize GPIOs.
  if (gpioInitialise() < 0)
    return 1;
  gpioSetMode(ModeGpio, PI_OUTPUT);    // Controls Peltier direction
  gpioSetMode(incInputGpio, PI_INPUT); // Increase setpoint.
  gpioSetMode(decInputGpio, PI_INPUT); // Decrease setpoint.

  // Callbacks for setpoint
  gpioSetAlertFunc(incInputGpio, increase_setpoint);
  gpioSetAlertFunc(decInputGpio, decrease_setpoint);

  // Initialize bcm2835 library
  if (!bcm2835_init())
  {
    cerr << "Initialize BCM2835 failed!" << endl;

    return -1;
  }

  // Set GPIO 4 to input with pullup
  bcm2835_gpio_fsel(4, BCM2835_GPIO_FSEL_INPT);
  bcm2835_gpio_set_pud(4, BCM2835_GPIO_PUD_UP);

  DS18B20 ds18b20;

  // Set fixed duty cycles
  duty_cycle_inner = 50;          // Inner fan
  duty_cycle_peltier_outer = 100; // Peltier and outer fan

  // Handle CTRL-C interrupt from keyboard.
  signal(SIGINT, inthand);

  while (!stop)
  {
    main_ready = false;
    worker_ready = false;

    std::thread worker(dt_control);
    start_time = std::chrono::system_clock::now();
    // Send data to the worker thread.
    {
      std::lock_guard<std::mutex> lk(m);
      main_ready = true;
    }
    cv.notify_one();

    // Keeping this should I want to recreate this with ds18b20
    // // Update temperature reading.
    // temp = 0;
    // samples = 20;
    // for (int j = 0; j < samples; ++j)
    // {
    //   // Average temperatures from all channels.
    //   for (std::size_t i = 0; i < channels.size(); ++i)
    //   {
    //     chan = channels[i];
    //     temps[chan] = get_temp(chan);
    //   }

    //   sum = std::accumulate(temps.begin(), temps.end(), 0.0);
    //   temp += (sum / channels.size());
    // }

    // // Average temperatures from all samples.
    // temp = temp / samples;

    // Get temp in celsius from ds18b20
    temp = ds18b20.readTemp();

    // If temperature too high, exit.
    if (temp > 40)
    {
      gpioHardwarePWM(PeltierPWM, 0, 0);
      printf("Temperature too high.");
      exit(EXIT_FAILURE);
    }

    // Don't update mode unless away from target temp or not in Rest
    if ((std::abs(temp - temp_target) > 1) || mode != "REST")
    {
      // Set direction and mode
      if (temp > temp_target)
      {
        if (mode == "HEAT")
        {
          flip_flop++;
        }
        else
        {
          gpioWrite(23, 1);
          mode = "COOL";
        }
      }
      else
      {
        if (mode == "COOL")
        {
          flip_flop++;
        }
        else
        {
          gpioWrite(23, 0);
          mode = "HEAT";
        }
      }
    }

    if (flip_flop > 0 || mode == "REST")
    {
      // Disable fans and Peltier near target temp.
      gpioHardwarePWM(FanPWM, 0, 0);
      gpioHardwarePWM(PeltierPWM, 0, 0);
      flip_flop = 0;
      mode = "REST";
    }
    else
    {
      gpioHardwarePWM(FanPWM, 5E5, (10000 * duty_cycle_inner));
      gpioHardwarePWM(PeltierPWM, 5E5, (10000 * duty_cycle_peltier_outer));
    }

    // Display and print temperature at reduced loop rate.
    if (loop_count == 0 || loop_count % 10 == 0)
    {
      std::string text =
          "Temp: " + std::to_string(static_cast<int>(round(temp))) + (char)247 +
          "C | " + mode + "ING\n" + "     (" + std::to_string(temp_target) +
          (char)247 + "C)";
      display_text(text.c_str());
      std::cout << text << std::endl;
    }

    std::cout << "Target: " << temp_target << std::endl;
    std::cout << "Temp: " << temp << std::endl;
    std::cout << "Mode: " << mode << std::endl;
    std::cout << "=============" << std::endl;

    // Wait for end of control cycle.
    {
      std::unique_lock<std::mutex> lk(m);
      cv.wait(lk, []
              { return worker_ready; });
    }
    worker.join();

    loop_count++;
  }

  gpioHardwarePWM(FanPWM, 0, 0);
  gpioHardwarePWM(PeltierPWM, 0, 0);
  display.close();
  gpioTerminate();

  return 0;
}
