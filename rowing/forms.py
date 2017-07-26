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
	
class CrewCompareForm(forms.Form):
	crew1 = AutoCompleteSelectMultipleField('crew', required=False, help_text=None, label="Crew 1")
	crew2 = AutoCompleteSelectMultipleField('crew', required=False, help_text=None, label="Crew 2")
	#crew1_name = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	#crew2_name = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	
class RankingForm(forms.Form):
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	g = forms.ChoiceField(label='Gender', required=True, choices=(('M','Men'),('W','Women')), widget=forms.Select(attrs={'class':'form-control'}))

class RowerForm(forms.Form):
	type = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	
class CompetitionForm(forms.Form):
	type = forms.ChoiceField(label='Type', required=False, choices=(('','Any'),('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
	raceclass = forms.ChoiceField(label='Class', required=False, choices=(('','Any'),('Senior','Senior'),('Club','Club')), widget=forms.Select(attrs={'class':'form-control'}))
	#event = forms.ChoiceField(label='Class', required=False, choices=(('','Any'),('O4-','O4-'),('O8+','O8+')), widget=forms.Select(attrs={'class':'form-control'})) - event needs to be pk not str
	year = forms.ChoiceField(label='Class', required=False, choices=(('','Any'),('2016','2016'),('2015','2015'),('2014','2014')), widget=forms.Select(attrs={'class':'form-control'}))