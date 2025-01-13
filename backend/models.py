class FinalSchedule(BaseModel):
    """Final schedule with ICS format details"""
    timestamp: datetime = Field(description="When this generation occurred")
    previous_step: ValidatedSchedule = Field(description="Output from previous step")
    calendar_properties: Dict[str, str] = Field(
        description="ICS calendar properties",
        example={
            "VERSION": "2.0",
            "PRODID": "-//Calendar++//Schedule Generator//EN",
            "CALSCALE": "GREGORIAN",
            "METHOD": "PUBLISH"
        }
    )
    events: List[Dict] = Field(description="List of ICS-formatted events")
    generation_notes: List[str] = Field(description="Notes about ICS generation process") 