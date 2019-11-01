from datetime import datetime
from datetime import timedelta
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from columns import ModelColumns

modelColumns = ModelColumns()


class InputSchema(Schema):
    """ /price - GET
    Parameters:
    - start (date)
    - end (date)
    - latitude (float)
    - longitude (float)
    - accommodates (int)
    - bedrooms (int)
    - beds (int)
    - room_type (int)
    - property_type (int)
    - cancellation_policy (int)
    - days_count (int)
    - days_list (array)
    """
    start = fields.Str(required=True)
    end = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    accommodates = fields.Int(required=True)
    bedrooms = fields.Int(required=True)
    beds = fields.Int(required=True)
    room_type = fields.Int(required=True)
    property_type = fields.Int(required=True)
    cancellation_policy = fields.Int(required=True)
    days_count = fields.Method("calc_days_count")
    days_list = fields.Method("make_days_list")

    def calc_days_count(self, data):
        start = datetime.strptime(data['start'], '%Y-%m-%d')
        end = datetime.strptime(data['end'], '%Y-%m-%d')
        return (end - start).days + 1

    def make_days_list(self, data):
        days_list = []
        start = datetime.strptime(data['start'], '%Y-%m-%d')
        for i in range(self.calc_days_count(data)):
            days_list.append(start + timedelta(days=i))
        return days_list

    @validates('start')
    def validate_start(self, value):
        try:
            start = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                "Incorrect data format, start should be YYYY-MM-DD.")

        min_limit = datetime.strptime('2009', '%Y')
        if start < min_limit:
            raise ValidationError(
                "Airbnb did not started, start should be 2009-01-01 or later.")

    @validates('end')
    def validate_end(self, value):
        try:
            end = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                "Incorrect data format, end should be YYYY-MM-DD.")

        max_limit = datetime.strptime('2030', '%Y')
        if end > max_limit:
            raise ValidationError("end should be before 2030-01-01.")

    @validates('latitude')
    def validate_latitude(self, value):
        south = 35.5014
        north = 35.8981
        if value < south or north < value:
            raise ValidationError(
                "latitude should be between {} and {} because learned data was Tokyo-to.".format(south, north))

    @validates('longitude')
    def validate_longitude(self, value):
        west = 138.9257
        east = 139.9156
        if value < west or east < value:
            raise ValidationError(
                "longitude should be between {} and {} because learned data was Tokyo-to.".format(west, east))

    @validates('accommodates')
    def validate_accommodates(self, value):
        if value < 0:
            raise ValidationError(
                "accommodates should be a positive value.")

    @validates('bedrooms')
    def validate_bedrooms(self, value):
        if value < 0:
            raise ValidationError(
                "bedrooms should be a positive value.")

    @validates('beds')
    def validate_beds(self, value):
        if value < 0:
            raise ValidationError(
                "beds should be a positive value.")

    @validates('room_type')
    def validate_room_type(self, value):
        columns = modelColumns.get_room_type_columns()
        min_index = min(columns.keys())
        max_index = max(columns.keys())
        if value < min_index or max_index < value:
            raise ValidationError(
                "room_type should be between {} and {}. definition:{}".format(min_index, max_index, columns))

    @validates('property_type')
    def validate_property_type(self, value):
        columns = modelColumns.get_property_type_columns()
        min_index = min(columns.keys())
        max_index = max(columns.keys())
        if value < min_index or max_index < value:
            raise ValidationError(
                "property_type should be between {} and {}. definition:{}".format(min_index, max_index, columns))

    @validates('cancellation_policy')
    def validate_cancellation_policy(self, value):
        columns = modelColumns.get_cancellation_policy_columns()
        min_index = min(columns.keys())
        max_index = max(columns.keys())
        if value < min_index or max_index < value:
            raise ValidationError(
                "cancellation_policy should be between {} and {}. definition:{}".format(min_index, max_index, columns))

    @validates_schema(skip_on_field_errors=True)
    def validate_data(self, data, **kwargs):
        start = datetime.strptime(data['start'], '%Y-%m-%d')
        end = datetime.strptime(data['end'], '%Y-%m-%d')
        if start > end:
            raise ValidationError(
                "Start date should be before end date.")
        days_count = self.calc_days_count(data)
        if days_count > 365:
            raise ValidationError(
                "The period between start and end should be less than 365 days.")
