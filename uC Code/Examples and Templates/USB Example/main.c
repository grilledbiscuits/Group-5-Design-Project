/**
  ******************************************************************************
  * @file    USB_Host/MSC_Standalone/Src/main.c
  * @author  MCD Application Team
  * @brief   USB host Mass storage demo main file
  ******************************************************************************
  ******************************************************************************
  */

/* Includes ----------------------------------------------------------------- */
#include "main.h"

/* Private typedef ---------------------------------------------------------- */
/* Private define ----------------------------------------------------------- */
/* Private macro ------------------------------------------------------------ */
/* Private variables -------------------------------------------------------- */
USBH_HandleTypeDef hUSBHost;
MSC_ApplicationTypeDef Appli_state = APPLICATION_IDLE;
char            USBDISKPath[4];            /* USB Host logical drive path */
FATFS           USBH_fatfs;
FIL             MyFile;
uint8_t         wtext[] = "USB Host Library : Mass Storage Example";
uint8_t         TransferBuffer[502];
//################################################################  
  FATFS         SDFatFs;  /* File system object for SD card logical drive */
  FIL           MySdFile;     /* File object */
  char          SDPath[4]; /* SD card logical drive path */
  char          USBPath[4];
  uint8_t       workBuffer[_MAX_SS];
  uint32_t      byteswritten, bytesread;                     /* File write/read counts */
  uint8_t       wSDtext[] = "I really like chocolate Ice-Cream.\r\n"; /* File write buffer */
  uint8_t       rSDtext[100];                                   /* File read buffer */  
  uint8_t       USB_State = 0;
  uint8_t       Fail_ctr = 0;
//################################################################ 

/* Private function prototypes ---------------------------------------------- */
static void SystemClock_Config(void);
static void USBH_UserProcess(USBH_HandleTypeDef * phost, uint8_t id);
void USB_StateMachine (void);
static void CPU_CACHE_Enable(void);
static void Error_Handler(void);

/* Private functions -------------------------------------------------------- */

/**
  * @brief  Main program
  * @param  None
  * @retval None
  */
int main(void)
{
  /* Enable the CPU Cache */
  CPU_CACHE_Enable();

  /* STM32F7xx HAL library initialization: - Configure the Flash ART
   * accelerator on ITCM interface - Configure the Systick to generate an
   * interrupt each 1 msec - Set NVIC Group Priority to 4 - Low Level
   * Initialization */
  HAL_Init();

  /* Configure the System clock to have a frequency of 200 MHz */
  SystemClock_Config();

  /* Init Host Library */
  USBH_Init(&hUSBHost, USBH_UserProcess, 0);

  /* Add Supported Class */
  USBH_RegisterClass(&hUSBHost, USBH_MSC_CLASS);

  /* Start Host Process */
  USBH_Start(&hUSBHost);

//################################################################  
  // Writing to SD card
  FATFS_LinkDriver(&SD_Driver, SDPath);
  f_mount(&SDFatFs, (TCHAR const*)SDPath, 1);   
  
  f_open(&MySdFile, "0:IceCream.txt", FA_READ | FA_WRITE | FA_OPEN_APPEND);
  f_write(&MySdFile, wSDtext, sizeof(wSDtext), (void *)&byteswritten);
  f_close(&MySdFile);
  
  f_open(&MySdFile, "0:IceCream.txt", FA_READ | FA_WRITE | FA_OPEN_APPEND);
  f_write(&MySdFile, wSDtext, sizeof(wSDtext), (void *)&byteswritten);
  f_close(&MySdFile);
  
  f_open(&MySdFile, "0:IceCream.txt", FA_READ | FA_WRITE | FA_OPEN_APPEND);
  f_write(&MySdFile, wSDtext, sizeof(wSDtext), (void *)&byteswritten);
  f_close(&MySdFile);
  
//  FATFS_UnLinkDriver(SDPath);
//################################################################   
  
  /* Run Application (Blocking mode) */
  while (1)
  {
    /* USB Host Background task */
    USBH_Process(&hUSBHost);

    /* MSC Menu Process */
    USB_StateMachine();
  }
}



/**
  * @brief  User Process
  * @param  phost: Host Handle
  * @param  id: Host Library user message ID
  * @retval None
  */
static void USBH_UserProcess(USBH_HandleTypeDef * phost, uint8_t id)
{
  switch (id)
  {
  case HOST_USER_SELECT_CONFIGURATION:
    break;

  case HOST_USER_DISCONNECTION:
    if (f_mount(NULL, "", 0) != FR_OK)
    {
        Fail_ctr++;
    }
    if (FATFS_UnLinkDriver(USBDISKPath) != 0)
    {
        Fail_ctr++;
    }
    USB_State = 1;
    break;

  case HOST_USER_CLASS_ACTIVE:
//    Appli_state = APPLICATION_READY;
    if( USB_State == 1 )
      USB_State = 2;
    break;

  case HOST_USER_CONNECTION:
    if (FATFS_LinkDriver(&USBH_Driver, USBDISKPath) == 0)
    {
      if (f_mount(&USBH_fatfs, (TCHAR const*)USBDISKPath, 0) != FR_OK)          // (TCHAR const*)USBDISKPath
      {
          Fail_ctr++;
      }
    }
    break;

  default:
    break;
  }
}

/****************************
*     USB State Machine     *
****************************/
void USB_StateMachine (void)
{
    uint16_t    i;
  
    switch( USB_State )
    {
        /**********************
        *      Init State     *
        **********************/
        case 0: 
        {
            USB_State = 1;
            break;
        }

        /**********************
        *      Wait State     *
        **********************/
        case 1:   
        {
            /*  Do Nothing  */
            break;
        }
        
        /**********************
        *  Create File State  *
        **********************/
        case 2:
        {
          if (f_open(&MyFile, "1:USBHost.txt", FA_CREATE_ALWAYS | FA_WRITE) != FR_OK)
            {
                Fail_ctr++;
            }
            else
            {
                f_write(&MyFile, wtext, sizeof(wtext), (void *)&byteswritten);
                f_close(&MyFile);
            }
            
            USB_State = 3;
            break;
        }      
        
        /**********************
        * Transfer File to SD *
        **********************/
        case 3:
        {
            f_open(&MyFile, "1:tfile.txt", FA_READ);
            f_open(&MySdFile, "0:New.txt", FA_CREATE_ALWAYS | FA_WRITE | FA_OPEN_APPEND);
            
            f_lseek(&MyFile, 0);
            for(i=0; i<3; i++)
            {  
                f_read(&MyFile, (void *)TransferBuffer, 100, (void *)&byteswritten );
                f_write(&MySdFile, TransferBuffer, 100, (void *)&byteswritten);
            }
            
            f_close(&MyFile);
            f_close(&MySdFile);
            
            
            USB_State = 4;
            break;
        } 
        
        /**********************
        *      End State      *
        **********************/
        case 4:   
        {
            /*  Ended - Do Nothing  */
            break;
        }        
        
    }
}


/**
  * @brief This function provides accurate delay (in milliseconds) based
  *        on SysTick counter flag.
  * @note This function is declared as __weak to be overwritten in case of other
  *       implementations in user file.
  * @param Delay: specifies the delay time length, in milliseconds.
  * @retval None
  */

void HAL_Delay(__IO uint32_t Delay)
{
  while (Delay)
  {
    if (SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk)
    {
      Delay--;
    }
  }
}

/**
  * @brief  Toggles LEDs to show user input state.
  * @param  None
  * @retval None
  */
void Toggle_Leds(void)
{
  static uint32_t ticks;

  if (ticks++ == 100)
  {
    BSP_LED_Toggle(LED1);
    ticks = 0;
  }
}

/**
  * @brief  System Clock Configuration
  *         The system Clock is configured as follow :
  *            System Clock source            = PLL (HSE)
  *            SYSCLK(Hz)                     = 200000000
  *            HCLK(Hz)                       = 200000000
  *            AHB Prescaler                  = 1
  *            APB1 Prescaler                 = 4
  *            APB2 Prescaler                 = 2
  *            HSE Frequency(Hz)              = 25000000
  *            PLL_M                          = 25
  *            PLL_N                          = 400
  *            PLL_P                          = 2
  *            PLLSAI_N                       = 384
  *            PLLSAI_P                       = 8
  *            VDD(V)                         = 3.3
  *            Main regulator output voltage  = Scale1 mode
  *            Flash Latency(WS)              = 7
  * @param  None
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_PeriphCLKInitTypeDef PeriphClkInitStruct;

  /* Enable HSE Oscillator and activate PLL with HSE as source */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSIState = RCC_HSI_OFF;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 400;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 8;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /* Activate the OverDrive to reach the 200 Mhz Frequency */
  if (HAL_PWREx_EnableOverDrive() != HAL_OK)
  {
    Error_Handler();
  }

  /* Select PLLSAI output as USB clock source */
  PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_CLK48;
  PeriphClkInitStruct.Clk48ClockSelection = RCC_CLK48SOURCE_PLLSAIP;
  PeriphClkInitStruct.PLLSAI.PLLSAIN = 192;
  PeriphClkInitStruct.PLLSAI.PLLSAIQ = 4;
  PeriphClkInitStruct.PLLSAI.PLLSAIP = RCC_PLLSAIP_DIV4;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2
   * clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                                 RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_6) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @param  None
  * @retval None
  */
static void Error_Handler(void)
{
  /* User may add here some code to deal with this error */
  while (1)
  {
  }
}

/**
  * @brief  CPU L1-Cache enable.
  * @param  None
  * @retval None
  */
static void CPU_CACHE_Enable(void)
{
  /* Enable I-Cache */
  SCB_EnableICache();

  /* Enable D-Cache */
  SCB_EnableDCache();
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t * file, uint32_t line)
{
  /* User can add his own implementation to report the file name and line
   * number, ex: printf("Wrong parameters value: file %s on line %d\r\n", file,
   * line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
