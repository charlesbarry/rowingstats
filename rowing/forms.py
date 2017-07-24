from django import forms
#from dal import autocomplete
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
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
	
class CompareForm(forms.Form):
	rower1 = AutoCompleteSelectField('crew', required=False, help_text=None, label="Rower 1")
	rower2 = AutoCompleteSelectField('crew', required=False, help_text=None, label="Rower 2")
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	
class RankingForm(forms.Form):
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	g = forms.ChoiceField(label='Gender', required=True, choices=(('M','Men'),('W','Women')), widget=forms.Select(attrs={'class':'form-control'}))

class RowerForm(forms.Form):
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))