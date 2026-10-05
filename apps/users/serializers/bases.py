from rest_framework import serializers

class StrictModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        allowed_input_fields = {
            field_name
            for field_name, field in self.fields.items()
            if not field.read_only
        }

        unexpected_fields = set(data.keys()) - allowed_input_fields

        if unexpected_fields:
            raise serializers.ValidationError({
                field: "Ce champ n'est pas autorisé."
                for field in unexpected_fields
            })

        return super().to_internal_value(data)