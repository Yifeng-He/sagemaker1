########### How to Develop step functions ########################
'''
Access to: https://www.draw.io/
Select Save Option (ex. Decide Later...)
Select Menu [Extras]-[Plugins]
Example
Drag and drop a Start on a diagram
Drag and drop a Task on a diagram
Select Task, and click a Settings(gear) icon, and Input params
Drag a connection from Start to Task
Drag and drop a End on a diagram
Drag a connection from Task to End
Menu [StepFunctions]-[Export JSON]
Copy the output and paste it to AWS Step Functions management console.
'''

######## How to periodically execute a step-function pipeline? #####
'''
https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-cloudwatch-events-target.html
you can specify the input to the stp fucntion in a json format
'''

###################################################################
#Execution results ##################################
#input to the step functions (load the input (input.json) from a S3 bucket)
{
    "A": 10,
    "B": 50,
    "D": 120
}

# input to the state 1 (a_plus_b)
{
  "A": 10,
  "B": 50,
  "D": 120
}
# output from state 1
{
  "A": 10,
  "B": 50,
  "D": 120,
  "result_state1": {
    "S": 60
  }
}
  
# input to state 2 (print_all)
{
  "A": 10,
  "B": 50,
  "D": 120,
  "result_state1": {
    "S": 60
  }
}  

#Amazon state machine for step fucntion
######################################################
{
  "StartAt": "a_plus_b",
  "States": {
    "a_plus_b": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:029716400694:function:aplusb",
      "Comment": "perform addition for A + B",
      "InputPath": "$",
      "OutputPath": "$",
      "ResultPath": "$.S_state1",
      "TimeoutSeconds": 60,
      "Next": "print_all",
      "Retry": [
        {
          "ErrorEquals": [
            "States.TaskFailed"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ]
    },
    "print_all": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:029716400694:function:print_results",
      "Comment": "print all elements in the inpt auguments",
      "OutputPath": "$",
      "TimeoutSeconds": 60,
      "End": true
    }
  }
}