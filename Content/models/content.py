from django.db import models
from django.db.models.constraints import UniqueConstraint
from Content.constants import CONTENT_TABLES


CONTENT_TABLES_CHOICE = [
    (CONTENT_TABLES.PERSONS, "Persons"),
    (CONTENT_TABLES.TERMS, "Terms"),
    (CONTENT_TABLES.DATES_RUS, "Dates rus"),
    (CONTENT_TABLES.MAPS, "Maps"),
    (CONTENT_TABLES.ARCHITECTURE, "Architecture"),
    (CONTENT_TABLES.LITERATURE, "Literature"),
    (CONTENT_TABLES.PICTURES, "Pictures"),
    (CONTENT_TABLES.SCULPTURE, "Sculpture"),
    (CONTENT_TABLES.HISTORY_TEXTS, "History texts"),
    (CONTENT_TABLES.THEORY, "Theory"),
    (CONTENT_TABLES.QUESTIONS, "Questions"),
    (CONTENT_TABLES.VIDEOS, "Videos"),
    (CONTENT_TABLES.DATES_WORLD, "Dates world"),
]


class ContentEntity(models.Model):
    wikidata_id = models.IntegerField(
        verbose_name="Wikidata identifier",
        help_text="Number in identifier (digits in (Q...))",
        unique=True, blank=True, null=True)
    table = models.SmallIntegerField(
        verbose_name="Content table of entity",
        choices=CONTENT_TABLES_CHOICE,
        null=True, blank=True,
    )
    index = models.IntegerField(verbose_name="Content table entity index", blank=True, null=True)
    name = models.CharField(
        verbose_name="Entity name",
        help_text="Name from content table (if exists)",
        max_length=250,
    )
    alternative_names = models.TextField(
        null=True, blank=True,
    )
    description = models.TextField(
        verbose_name="Very short description about entity",
        help_text="Description (without name) from preview function for entity table",
        null=True, blank=True,
    )
    text = models.TextField(
        verbose_name="Very short text about entity",
        help_text="Text (with name) from preview function for entity table",
        null=True, blank=True,
    )
    image = models.TextField(blank=True, null=True)
    rank = models.IntegerField(
        help_text="Rank for rank algorithms to sort entities",
        default=1,
    )

    class Meta:
        constraints = [UniqueConstraint(fields=['table', 'index'], name='table_index_unique')]

    def __str__(self):
        s = ""
        if self.wikidata_id:
            s += f"(Q{self.wikidata_id}) "
        else:
            s += f"(Q---) "
        if self.index and self.table:
            s += f"{self.table[:2]}{self.index} "
        else:
            s += f"XX---- "
        s += self.name[:60]
        return s


class ContentEvent(models.Model):
    name = models.CharField(verbose_name='Event name', max_length=250)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Event date', max_length=80)
    information = models.TextField(verbose_name='Additional information about event', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentTerm(models.Model):
    name = models.CharField(verbose_name='Term name', max_length=100)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    definition = models.TextField(verbose_name='Definition of the term')
    information = models.TextField(verbose_name='Additional information about term', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


# + table of relations with dates
class ContentPerson(models.Model):
    name = models.CharField(verbose_name='Person name', max_length=200)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    another_names = models.TextField(verbose_name='Another names of person', blank=True)
    summary = models.TextField(verbose_name='Person summary', blank=True)
    dates_of_life = models.CharField(verbose_name='Dates of life', max_length=100, blank=True)
    board_time = models.CharField(verbose_name='Time of the board', max_length=100, blank=True)
    image = models.TextField(verbose_name='Link to the image', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    information = models.TextField(verbose_name='Information about person', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentArchitecture(models.Model):
    name = models.CharField(verbose_name='Architecture name', max_length=120)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    founder = models.CharField(verbose_name='Founder', max_length=120, blank=True)
    architect = models.CharField(verbose_name='Architect', max_length=120, blank=True)
    city = models.CharField(verbose_name='City', max_length=100, blank=True)
    style = models.CharField(verbose_name='Style', max_length=100, blank=True)
    image = models.TextField(verbose_name='Link to the image', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    information = models.TextField(verbose_name='Information', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentPicture(models.Model):
    name = models.CharField(verbose_name='Architecture name', max_length=120)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    author = models.CharField(verbose_name='Author', max_length=120, blank=True)
    image = models.TextField(verbose_name='Link to the image of picture', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    information = models.TextField(verbose_name='Information', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentSculpture(models.Model):
    name = models.CharField(verbose_name='Sculpture name', max_length=120)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    author = models.CharField(verbose_name='Author', max_length=120, blank=True)
    city = models.CharField(verbose_name='City', max_length=100, blank=True)
    image = models.TextField(verbose_name='Link to the image of sculpture', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    information = models.TextField(verbose_name='Information', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentLiterature(models.Model):
    name = models.CharField(verbose_name='Literature name', max_length=120)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    author = models.CharField(verbose_name='Author', max_length=120, blank=True)
    image = models.TextField(verbose_name='Link to the image of literature', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    information = models.TextField(verbose_name='Information', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentMap(models.Model):
    name = models.CharField(verbose_name='Map name', max_length=120)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    image = models.TextField(verbose_name='Link to the image of map', blank=True)
    image_100 = models.URLField(verbose_name="Image with width 100px", max_length=300, null=True, blank=True)
    task_image = models.TextField(verbose_name='Link to the image of task with map', blank=True)
    information = models.TextField(verbose_name='Information', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class ContentHistoryText(models.Model):
    name = models.CharField(verbose_name='Text name', max_length=150)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(verbose_name='Date', max_length=70, blank=True)
    is_full = models.BooleanField(verbose_name='Is full text')
    text = models.TextField(verbose_name='History text')
    information = models.TextField(verbose_name='Information', blank=True)
    recognize_hint = models.TextField(verbose_name='Recognize hint', blank=True)

    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['index']


class VideoInformation(models.Model):
    name = models.CharField(verbose_name='Video name', max_length=120)
    key = models.CharField(verbose_name='Youtube video key', max_length=100)
    image = models.TextField(verbose_name='Link to the image of video')
    duration = models.IntegerField(verbose_name='Video duration', default=0)

    def __str__(self):
        return self.name


class ContentVideo(models.Model):
    name = models.CharField(verbose_name='Name', max_length=120, blank=True)
    index = models.IntegerField(verbose_name='Unique index', unique=True)
    entity = models.ForeignKey('Content.ContentEntity', on_delete=models.SET_NULL, null=True, blank=True)
    video = models.ForeignKey('VideoInformation', on_delete=models.CASCADE, verbose_name='Video')
    image = models.TextField(verbose_name='Link to the image of video', blank=True)
    time_code = models.IntegerField(verbose_name='Time code', default=0)

    def __str__(self):
        return self.name if self.name else self.video.name


class ContentIndexRelationship(models.Model):
    first_index = models.IntegerField(verbose_name='First index')
    first_code = models.CharField(verbose_name='First code of table', max_length=2)
    second_index = models.IntegerField(verbose_name='Second index')
    second_code = models.CharField(verbose_name='Second code of table', max_length=2)
