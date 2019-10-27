class ModelColumns():
    input_columns = ["holiday", "month_1", "month_2", "month_3", "month_4", "month_5", "month_6", "month_7", "month_8", "month_9", "month_10", "month_11", "month_12", "day_of_week_0", "day_of_week_1", "day_of_week_2", "day_of_week_3", "day_of_week_4", "day_of_week_5", "day_of_week_6", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6", "day_7", "day_8", "day_9", "day_10", "day_11", "day_12", "day_13", "day_14", "day_15", "day_16", "day_17", "day_18", "day_19", "day_20", "day_21", "day_22", "day_23", "day_24", "day_25", "day_26", "day_27", "day_28", "day_29", "day_30", "day_31", "accommodates", "bedrooms", "beds", "property_type_Apartment", "property_type_House", "property_type_Serviced apartment", "property_type_Condominium", "property_type_Guest suite", "property_type_Hut", "property_type_Tiny house", "property_type_Townhouse", "property_type_Villa", "property_type_Aparthotel", "property_type_Cabin", "property_type_Bed and breakfast", "property_type_Loft", "property_type_Hostel", "property_type_Guesthouse", "property_type_Boutique hotel", "property_type_Nature lodge", "property_type_Ryokan (Japan)", "property_type_Tent", "property_type_Hotel", "property_type_Bungalow", "property_type_Other", "property_type_Camper/RV", "property_type_Boat", "property_type_Dome house", "property_type_Dorm", "property_type_Resort", "property_type_Barn", "room_type_Private room", "room_type_Entire home/apt", "room_type_Shared room", "cancellation_policy_strict_14_with_grace_period", "cancellation_policy_moderate", "cancellation_policy_flexible", "cancellation_policy_super_strict_30", "cancellation_policy_super_strict_60", "cancellation_policy_strict", "neighborhood_colloquial_area", "neighborhood_book_store", "neighborhood_cafe", "neighborhood_restaurant", "neighborhood_hair_care", "neighborhood_bar", "neighborhood_locality", "neighborhood_food", "neighborhood_lodging", "neighborhood_point_of_interest", "neighborhood_grocery_or_supermarket", "neighborhood_funeral_home", "neighborhood_finance", "neighborhood_health", "neighborhood_beauty_salon", "neighborhood_primary_school", "neighborhood_lawyer", "neighborhood_church", "neighborhood_general_contractor", "neighborhood_electrician", "neighborhood_school", "neighborhood_real_estate_agency", "neighborhood_laundry", "neighborhood_gym",
                     "neighborhood_bicycle_store", "neighborhood_car_repair", "neighborhood_dentist", "neighborhood_home_goods_store", "neighborhood_library", "neighborhood_car_dealer", "neighborhood_pet_store", "neighborhood_meal_takeaway", "neighborhood_meal_delivery", "neighborhood_gas_station", "neighborhood_bakery", "neighborhood_travel_agency", "neighborhood_parking", "neighborhood_store", "neighborhood_post_office", "neighborhood_florist", "neighborhood_clothing_store", "neighborhood_doctor", "neighborhood_insurance_agency", "neighborhood_shoe_store", "neighborhood_tourist_attraction", "neighborhood_art_gallery", "neighborhood_convenience_store", "neighborhood_secondary_school", "neighborhood_park", "neighborhood_supermarket", "neighborhood_movie_rental", "neighborhood_place_of_worship", "neighborhood_hospital", "neighborhood_electronics_store", "neighborhood_embassy", "neighborhood_night_club", "neighborhood_jewelry_store", "neighborhood_cemetery", "neighborhood_atm", "neighborhood_pharmacy", "neighborhood_sublocality_level_2", "neighborhood_furniture_store", "neighborhood_liquor_store", "neighborhood_museum", "neighborhood_drugstore", "neighborhood_storage", "neighborhood_veterinary_care", "neighborhood_shopping_mall", "neighborhood_spa", "neighborhood_bank", "neighborhood_university", "neighborhood_locksmith", "neighborhood_moving_company", "neighborhood_fire_station", "neighborhood_police", "neighborhood_hardware_store", "neighborhood_accounting", "neighborhood_painter", "neighborhood_car_rental", "neighborhood_sublocality_level_3", "neighborhood_transit_station", "neighborhood_department_store", "neighborhood_movie_theater", "neighborhood_city_hall", "neighborhood_train_station", "neighborhood_bowling_alley", "neighborhood_local_government_office", "neighborhood_roofing_contractor", "neighborhood_sublocality_level_1", "neighborhood_synagogue", "neighborhood_car_wash", "neighborhood_stadium", "neighborhood_plumber", "neighborhood_natural_feature", "neighborhood_aquarium", "neighborhood_amusement_park", "neighborhood_subway_station", "neighborhood_zoo", "neighborhood_physiotherapist", "neighborhood_campground", "neighborhood_casino", "neighborhood_airport", "neighborhood_courthouse", "neighborhood_taxi_stand", "neighborhood_premise", "neighborhood_mosque"]

    def get_input_columns(self):
        return self.input_columns

    __room_type_columns = {
        1: "room_type_Private room",
        2: "room_type_Entire home/apt",
        3: "room_type_Shared room"
    }

    def get_room_type_columns(self):
        return self.__room_type_columns

    def get_room_type_column_name(self, key):
        if key in self.__room_type_columns:
            return self.__room_type_columns[key]
        return False

    __property_type_columns = {
        1: "property_type_Apartment",
        2: "property_type_House",
        3: "property_type_Serviced apartment",
        4: "property_type_Condominium",
        5: "property_type_Guest suite",
        6: "property_type_Hut",
        7: "property_type_Tiny house",
        8: "property_type_Townhouse",
        9: "property_type_Villa",
        10: "property_type_Aparthotel",
        11: "property_type_Cabin",
        12: "property_type_Bed and breakfast",
        13: "property_type_Loft",
        14: "property_type_Hostel",
        15: "property_type_Guesthouse",
        16: "property_type_Boutique hotel",
        17: "property_type_Nature lodge",
        18: "property_type_Ryokan (Japan)",
        19: "property_type_Tent",
        20: "property_type_Hotel",
        21: "property_type_Bungalow",
        22: "property_type_Other",
        23: "property_type_Camper/RV",
        24: "property_type_Boat",
        25: "property_type_Dome house",
        26: "property_type_Dorm",
        27: "property_type_Resort",
        28: "property_type_Barn"
    }

    def get_property_type_columns(self):
        return self.__property_type_columns

    def get_property_type_column_name(self, key):
        if key in self.__property_type_columns:
            return self.__property_type_columns[key]
        return False

    __cancellation_policy_columns = {
        1: "cancellation_policy_strict_14_with_grace_period",
        2: "cancellation_policy_moderate",
        3: "cancellation_policy_flexible",
        4: "cancellation_policy_super_strict_30",
        5: "cancellation_policy_super_strict_60",
        6: "cancellation_policy_strict"
    }

    def get_cancellation_policy_columns(self):
        return self.__cancellation_policy_columns

    def get_cancellation_policy_column_name(self, key):
        if key in self.__cancellation_policy_columns:
            return self.__cancellation_policy_columns[key]
        return False
