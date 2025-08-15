from django import forms

import my_app.models as m


class UserTaskBlockForm(forms.ModelForm):
    class Meta:
        model = m.UserTask
        fields = [
            "blocked_by",
            "status",
            "user",
            # "reported_blocked_by",
        ]

    def __init__(self, *args, **kwargs):
        potential_blocking_tasks = kwargs.pop("potential_blocking_tasks", None)
        super().__init__(*args, **kwargs)

        if potential_blocking_tasks is not None:
            self.fields["blocked_by"].queryset = potential_blocking_tasks
