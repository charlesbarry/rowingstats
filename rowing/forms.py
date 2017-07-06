from django import forms
#from dal import autocomplete
from ajax_select.fields import AutoCompleteSelectMultipleField
from rowing.models import Rower, Result

# a manual form
class TestForm(forms.Form):
	your_name = forms.CharField(label='Your name', max_length=100)
	
# an example of ModelForm
class ExampleForm(forms.ModelForm):
	class Meta:
		model = Rower
		
		# indicates all fields to be used
		fields = '__all__'
		
		# exclude a field
		exclude = ['name']
	
class ResultForm(forms.ModelForm):
	class Meta:
		model = Result
		fields = '__all__'
		
	crew = AutoCompleteSelectMultipleField('crew', required=True, help_text="Add crew members")
	clubs = AutoCompleteSelectMultipleField('clubs', required=True, help_text="Add club (or multiple for composite)")
	