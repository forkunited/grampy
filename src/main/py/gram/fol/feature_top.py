from gram import feature

class FeatureTopToken(feature.FeatureToken):
    def __init__(self):
        feature.FeatureToken.__init__(self)

    def __str__(self):
        return "T"

    def init_start(self):
        pass

    def init_datum(self, datum):
        pass

    def init_end(self):
        pass


class FeatureTopType(feature.FeatureType):
    def __init__(self):
        feature.FeatureType.__init__(self)

    def compute(self, datum):
        return [1.0]

    def get_size(self):
        return 1

    def get_token(self, index):
        return FeatureTopToken()

    def equals(self, feature_type):
        return isinstance(feature_type, FeatureTopType)

    def init_start(self):
        pass

    def init_datum(self, datum):
        pass

    def init_end(self):
        pass
