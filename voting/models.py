from django.db import models

# Create your models here.
from django.db.models import Sum


class Party(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=80)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=80)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    is_provincial_capital = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class VotingCenter(models.Model):
    name = models.CharField(max_length=50)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.name, self.district)


class VotingTable(models.Model):
    number = models.CharField(max_length=6, primary_key=True)
    total_voters = models.IntegerField()
    voting_center = models.ForeignKey(VotingCenter, on_delete=models.CASCADE)
    is_presidential_processed = models.BooleanField(default=False)
    is_congress_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.number


class ElectoralAct(models.Model):
    voting_table = models.OneToOneField(VotingTable, primary_key=True, on_delete=models.CASCADE)
    blank_votes = models.IntegerField()
    void_votes = models.IntegerField()
    contested_votes = models.IntegerField()
    emitted_votes = models.IntegerField()

    def valid_votes(self):
        valid_votes = self.emitted_votes - self.contested_votes - self.void_votes - self.blank_votes
        return valid_votes

    def __str__(self):
        return self.voting_table.number


class DetailElectoralAct(models.Model):
    electoral_act = models.ForeignKey(ElectoralAct, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    votes = models.IntegerField()

    class Meta:
        unique_together = (('electoral_act', 'party'),)

    def __str__(self):
        return self.electoral_act.voting_table.number + " " + self.party.name


class DesignElectoralAct(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DetailDesignElectoralAct(models.Model):
    design_electoral_act = models.ForeignKey(DesignElectoralAct, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    location = models.IntegerField()

    def __str__(self):
        return self.party.name


class PresidentElectionResults(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.party

    def porcentaje(self):
        total = PresidentElectionResults.objects.all().aggregate(Sum('votes'))
        return round(self.votes * 100.00 / total['votes__sum'], 2)
