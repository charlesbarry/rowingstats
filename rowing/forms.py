from django import forms
#from dal import autocomplete
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from rowing.models import Rower, Result, Club

type_choices = (
        ('Sweep', 'Sweep'),
        ('Sculling', 'Sculling'),
        ('Lwt Sweep', 'Lightweight Sweep'),
        ('Lwt Sculling', 'Lightweight Sculling'),
        ('Para-Sweep', 'Para-Sweep'),
        ('Para-Sculling', 'Para-Sculling'),
    )

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
        
    crew = AutoCompleteSelectMultipleField('crew', required=False, help_text="Add crew members")
    clubs = AutoCompleteSelectMultipleField('clubs', required=False, help_text="Add club (or multiple for composite)")
    cox = AutoCompleteSelectField('cox', required=False, help_text=None, label="Cox")
    
class CompareForm(forms.Form):
    rower1 = AutoCompleteSelectField('crew', required=False, help_text=None, label="Rower 1")
    rower2 = AutoCompleteSelectField('crew', required=False, help_text=None, label="Rower 2")
    type = forms.ChoiceField(label='Type', required=True, choices=type_choices, widget=forms.Select(attrs={'class':'form-control'}))
    
class CrewCompareForm(forms.Form):
    crew1 = AutoCompleteSelectMultipleField('crew', required=False, help_text=None, label="Crew 1")
    crew2 = AutoCompleteSelectMultipleField('crew', required=False, help_text=None, label="Crew 2")
    #crew1_name = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
    #crew2_name = forms.ChoiceField(label='Type', required=True, choices=(('Sweep','Sweep'),('Sculling','Sculling')), widget=forms.Select(attrs={'class':'form-control'}))
    type = forms.ChoiceField(label='Type', required=True, choices=type_choices, widget=forms.Select(attrs={'class':'form-control'}))
    
class WeatherForm(forms.Form):
    v1 = forms.FloatField(label='Initial speed', required=True)
    water_temp1 = forms.FloatField(required=True)
    air_temp1 = forms.FloatField(label='Initial speed', required=True)
    air_pressure1 = forms.FloatField(label='Initial speed', required=True)
    air_humidity1 = forms.FloatField(label='Initial speed', required=True)
    water_flow1 = forms.FloatField(label='Initial speed', required=True)
    wind_v1 = forms.FloatField(label='Initial speed', required=True)
    wind_angle1 = forms.FloatField(label='Initial speed', required=True)
    cd_air1 = forms.FloatField(label='Initial speed', required=True)
    A_air1 = forms.FloatField(label='Initial speed', required=True)
    A_water1 = forms.FloatField(label='Initial speed', required=True)
    boat_length1 = forms.FloatField(label='Initial speed', required=True)

    water_temp2 = forms.FloatField(label='Initial speed', required=True)
    air_temp2 = forms.FloatField(label='Initial speed', required=True)
    air_pressure2 = forms.FloatField(label='Initial speed', required=True)
    air_humidity2 = forms.FloatField(label='Initial speed', required=True)
    water_flow2 = forms.FloatField(label='Initial speed', required=True)
    wind_v2 = forms.FloatField(label='Initial speed', required=True)
    wind_angle2 = forms.FloatField(label='Initial speed', required=True)
    cd_air2 = forms.FloatField(label='Initial speed', required=True)
    A_air2 = forms.FloatField(label='Initial speed', required=True)
    A_water2 = forms.FloatField(label='Initial speed', required=True)
    boat_length2 = forms.FloatField(label='Initial speed', required=True)

class RankingForm(forms.Form):
    type = forms.ChoiceField(label='Type', required=True, choices=type_choices, widget=forms.Select(attrs={'class':'form-control'}))
    g = forms.ChoiceField(label='Gender', required=True, choices=(('M','Men'),('W','Women')), widget=forms.Select(attrs={'class':'form-control'}))
    current = forms.ChoiceField(label='Current', required=True, choices=(('y','Current results'),('n','All time')), widget=forms.Select(attrs={'class':'form-control'}))
    gb = forms.ChoiceField(label='GB Only?', required=True, choices=(('y','GB Only'),('n','All / International')), widget=forms.Select(attrs={'class':'form-control'}))

class RowerForm(forms.Form):
    type = forms.ChoiceField(label='Type', required=True, choices=type_choices, widget=forms.Select(attrs={'class':'form-control'}))
    
class CompetitionForm(forms.Form):
    # some magic to create dynamic fields - I don't understand it
    #super(CompetitionForm, self).__init__(*args, **kwargs)
    def __init__(self, class_choices, event_choices, year_choices, *args, **kwargs):
        super(CompetitionForm, self).__init__(*args, **kwargs)
        self.fields["raceclass"].choices = class_choices
        self.fields["event"].choices = event_choices
        self.fields["year"].choices = year_choices

    type = forms.ChoiceField(label='Type', required=False, choices=((('','Any'),) + type_choices), widget=forms.Select(attrs={'class':'form-control'}))
    
    # choices was = (('','Any'),('Senior','Senior'),('Club','Club'))
    raceclass = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))
    event = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))
    year = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))
    
class ClubForm(forms.Form):
    # copied from CompetitionForm so errors doubtless abound
    def __init__(self, year_choices, *args, **kwargs):
        super(CompetitionForm, self).__init__(*args, **kwargs)
        self.fields["year"].choices = year_choices

    year = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))
    
class FixtureEditionForm(forms.Form):
    def __init__(self, edition_choices, *args, **kwargs):
        super(FixtureEditionForm, self).__init__(*args, **kwargs)
        self.fields["edition"].choices = edition_choices
        
    edition = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))

class FixtureEventForm(forms.Form):
    def __init__(self, event_choices, *args, **kwargs):
        super(FixtureEventForm, self).__init__(*args, **kwargs)
        self.fields["event"].choices = event_choices

    event = forms.ChoiceField(label='Class', required=False, choices=(), widget=forms.Select(attrs={'class':'form-control'}))