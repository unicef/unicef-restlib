from unicef_restlib.fields import ModelChoiceField


class FileTypeModelChoiceField(ModelChoiceField):
    def get_choice(self, obj):
        return obj.pk, obj.name
