from gram import feature

class FeatureFormIndicatorToken(feature.FeatureToken):
    def __init__(self, closed_form):
        feature.FeatureToken.__init__(self)
        self._closed_form = closed_form

    def get_closed_form(self):
        return self._closed_form

    def __str__(self):
        return str(self._closed_form)


class FeatureFormIndicatorType(feature.FeatureType):
    def __init__(self, open_form):
        feature.FeatureType.__init__(self)
        self._open_form = open_form

    def get_open_form(self):
        return self._open_form

    def compute(self, datum):
        closed_forms = self._open_form.get_closed_forms()
        expr = self._open_form.get_form()
        return [1.0 if datum.get_model().evaluate(expr, c.get_g()) else 0.0 for c in closed_forms]

    def get_size(self):
        return len(self._open_form.get_closed_forms())

    def get_token(self, index):
        return FeatureFormIndicatorToken(self._open_form.get_closed_forms()[index])

    def equals(self, feature_type):
        my_g = self._open_form.get_init_g()
        g = feature_type.get_open_form().get_init_g()

        for v in my_g:
            if v not in g or g[v] != my_g[v]:
                return False

        return self._open_form.exp_matches(feature_type.get_open_form())

