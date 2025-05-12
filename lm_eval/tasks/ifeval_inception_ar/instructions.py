from lm_eval.tasks.ifeval import instructions 

class AragenInstructions(instructions.Instruction):
    def __init__(self, instruction_id):
        super().__init__(instruction_id)

    def build_description(self, **kwargs):
        return "No kwargs needed just pass in the response and check if it is correct"

    def get_instruction_args(self):
        return {}
    
    def get_instruction_args_keys(self):
        return []
    

class DataIdx1InstructionChecker(AragenInstructions):
    def __init__(self):
        super().__init__("idx_1")
    
    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        return 

    
    
    