from canvas_sdk.effects.custom_model.mutation import Mutation


class Delete(Mutation):
    def apply(self):
        # Perform security checks and proceed if they clear
        self.qs.delete()


__exports__ = "Delete"
