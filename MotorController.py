#this needs to connect to the control board and identify the two motors, we will now call them 'a' and 'b'
# we need a function to position the motors to a specific value
# we need a zero/calibration function
#we need a translate function that uses the set optical powers to keep the ocom aligned to the optical axis
displacement_per_step = 0.46e-9
import numpy as np
class MotorController:
    def __init__(self, stage_length):
        """Initialize the MotorController with the specified serial port."""
        from pylablib.devices import Thorlabs
        stages= Thorlabs.list_kinesis_devices()
        self.stageA = Thorlabs.KinesisMotor(stages[0][0], is_rack_system=False)
        self.stageB = Thorlabs.KinesisMotor(stages[1][0], is_rack_system=False)
        self.method = self.NonLinearOCOMLock
        self.stage_length = stage_length  # in meters

    def Set_Separation(self, separation_wr, power_chA_w, power_chB_w, waist_radius_m):
            success = True
            fixed_translation_wr, variable_translation_wr = self.method(separation_wr, power_chA_w, power_chB_w)
            #convert to meters
            fixed_translation = fixed_translation_wr * waist_radius_m
            variable_translation = variable_translation_wr * waist_radius_m
            verbose = False
            if verbose:
                print(f"power ratio is {power_chB_w/power_chA_w}")
                print(f"target separation is {separation_wr} wr")
                print(f"Channel A separation set to {fixed_translation} m")
                print(f"Channel B separation set to {variable_translation} m")
                print(f"total separation set to {(fixed_translation + variable_translation)/waist_radius_m} wr")
                ocom = fixed_translation*power_chA_w - variable_translation*power_chB_w
                print(f"weight centre of mass", ocom)
            if (fixed_translation > self.stage_length) or (variable_translation > self.stage_length):
                print("Warning: Requested separation exceeds stage length. Reconsider your choice of separations")
                success = False
            else:
                self.stageA.move_to((fixed_translation) / displacement_per_step)
                self.stageB.move_to((variable_translation) / displacement_per_step) #we align this to be 6mm offset
                # print(f"({3e-3 + variable_translation}), ", f"{(3e-3 + fixed_translation)})")
                self.stageA.wait_move()
                self.stageB.wait_move()

            return success


    def NonLinearOCOMLock(self, separation_wr, power_chA_w, power_chB_w):
        """Non-linear OCOM lock method to adjust the separation based on optical powers."""

        power_ratio_r = power_chB_w/power_chA_w
        if power_ratio_r == 1:
            return separation_wr/2, separation_wr/2  # If the powers are equal, we can just split the separation evenly
        #if the power ratios are equal, we overide this
        # print("power_ratio", power_ratio_r)
        fixed_source_translation =separation_wr* (1 - 1 / (1 + power_ratio_r))
        variable_source_translation =  separation_wr *  1/ (1 + power_ratio_r)
        return fixed_source_translation, variable_source_translation

if __name__ == "__main__":
        from pylablib.devices import Thorlabs
        stages= Thorlabs.list_kinesis_devices()

        print(stages)
        motor_controller = MotorController(stage_length=6e-3)
        motor_controller.stageA.move_to(0/displacement_per_step)
        motor_controller.stageB.move_to(0/displacement_per_step)
        print("moving")
