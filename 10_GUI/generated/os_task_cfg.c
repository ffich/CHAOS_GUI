/************************************************************************
*                               OS Task Cfg                         
*************************************************************************
* FileName:         os_task_cfg.c                                                                                
* Author:           F.Ficili                                            
*                                                                       
* Software License Agreement:                                           
*                                                                       
* THIS SOFTWARE IS PROVIDED IN AN "AS IS" CONDITION. NO WARRANTIES,     
* WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT LIMITED     
* TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A           
* PARTICULAR PURPOSE APPLY TO THIS SOFTWARE. THE AUTHOR SHALL NOT,      
* IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR            
* CONSEQUENTIAL DAMAGES, FOR ANY REASON WHATSOEVER.                     
*                                                                       
* --------------------------------------------------------------------- 
* File History:                                                                                         
* --------------------------------------------------------------------- 
* Author       Date        Version      Comment                         
* ---------------------------------------------------------------------	
*             
************************************************************************/

/************************************************************************
* Includes
************************************************************************/
#include "os_task.h"
#include "os_task_cfg.h"

/************************************************************************
* Typedefs
************************************************************************/


/************************************************************************
* LOCAL Variables
************************************************************************/


/************************************************************************
* TASK List
************************************************************************/
extern void Led_Task (void);
extern void Task_1 (void);
extern void Task_2 (void);
extern void Task_3 (void);
extern void Task_4 (void);
extern void Task_5 (void);

/************************************************************************
* GLOBAL Variables
************************************************************************/
TbcType Tasks [] =
{
  /* -------------------------------------------------------------------- */
  /* ID                    Task              State           Priority     */
  /* -------------------------------------------------------------------- */   
  /* --------------------------------- Tasks ---------------------------- */   
  {Led_Task_ID,           Led_Task,         IDLE,           1},
  {Task_1_ID,           Task_1,         IDLE,           1},
  {Task_2_ID,           Task_2,         IDLE,           1},
  {Task_3_ID,           Task_3,         IDLE,           1},
  {Task_4_ID,           Task_4,         IDLE,           1},
  {Task_5_ID,           Task_5,         IDLE,           1},
  /* -------------------------------------------------------------------- */
};

/* Auto-calculation of task number */
const uint16_t TaskNumber = (uint16_t)(sizeof(Tasks)/sizeof(TbcType));  

/* List of auto-started Tasks */
AutoStarTaskType AutoStartedTasks[] =
{
};

/* Auto-calculation of auto-started task number */
const uint16_t AutoStartTaskNumber = (uint16_t)(sizeof(AutoStartedTasks)/sizeof(AutoStarTaskType));  

/************************************************************************
* LOCAL Functions
************************************************************************/


/************************************************************************
* GLOBAL Functions
************************************************************************/
