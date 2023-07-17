class MacBookVO:
    def __init__(self, model: str = "", screen_size: int = -1,
                 chip: str = "", cpu_core: int = -1, gpu_core: int = -1,
                 ram: str = "", ssd: str = "",
                 apple_care_plus: bool = False, unopened: bool = False):
        self.model = model
        self.screen_size = screen_size
        self.chip = chip
        self.cpu_core = cpu_core
        self.gpu_core = gpu_core
        self.ram = ram
        self.ssd = ssd
        self.apple_care_plus = apple_care_plus
        self.unopened = unopened

    def __str__(self):
        return "MacBook(model={}, screen_size={}, chip={}, cpu_core={}, gpu_core={}, ram={}, ssd={}, apple_care_plus={}, unopened={})".format(
            self.model, self.screen_size, self.chip, self.cpu_core, self.gpu_core, self.ram, self.ssd,
            self.apple_care_plus, self.unopened
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'model': self.model,
            'screen_size': self.screen_size,
            'chip': self.chip,
            'cpu_core': self.cpu_core,
            'gpu_core': self.gpu_core,
            'ram': self.ram,
            'ssd': self.ssd,
            'apple_care_plus': self.apple_care_plus,
            'unopened': self.unopened
        }

    @staticmethod
    def from_dict(d) -> 'MacBookVO':
        try:
            return MacBookVO(
                model=d['model'],
                screen_size=d['screen_size'],
                chip=d['chip'],
                cpu_core=d['cpu_core'],
                gpu_core=d['gpu_core'],
                ram=d['ram'],
                ssd=d['ssd'],
                apple_care_plus=d['apple_care_plus'],
                unopened=d['unopened']
            )
        except KeyError as e:
            raise ValueError('Invalid MacBookVO: missing key {}'.format(e.args[0]))

    def update(self, macbook_model):
        if type(macbook_model) is MacBookModelVO:
            self.model = macbook_model.model
            self.screen_size = macbook_model.screen_size
        elif type(macbook_model) is MacBookModelDetailVO:
            self.chip = macbook_model.chip
            self.cpu_core = macbook_model.cpu_core
            self.gpu_core = macbook_model.gpu_core
        elif type(macbook_model) is MacBookSystemVO:
            self.ram = macbook_model.ram
            self.ssd = macbook_model.ssd


class MacBookModelVO:

    def __init__(self, model: str = "", screen_size: int = -1):
        self.model = model
        self.screen_size = screen_size

    def __str__(self):
        return "MacBookModel(model={}, screen_size={})".format(
            self.model, self.screen_size
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'model': self.model,
            'screen_size': self.screen_size
        }

    @staticmethod
    def from_dict(d) -> 'MacBookModelVO':
        try:
            return MacBookModelVO(
                model=d['model'],
                screen_size=d['screen_size']
            )
        except KeyError as e:
            return MacBookModelVO()


class MacBookModelDetailVO:

    def __init__(self, chip: str = "", cpu_core: int = -1, gpu_core: int = -1):
        self.chip = chip
        self.cpu_core = cpu_core
        self.gpu_core = gpu_core

    def __str__(self):
        return "MacBookModelDetail(chip={}, cpu_core={}, gpu_core={})".format(
            self.chip, self.cpu_core, self.gpu_core
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'chip': self.chip,
            'cpu_core': self.cpu_core,
            'gpu_core': self.gpu_core
        }

    @staticmethod
    def from_dict(d) -> 'MacBookModelDetailVO':
        try:
            return MacBookModelDetailVO(
                chip=d['chip'],
                cpu_core=d['cpu_core'],
                gpu_core=d['gpu_core']
            )
        except KeyError as e:
            return MacBookModelDetailVO()


class MacBookSystemVO:
    def __init__(self, ram: str = "", ssd: str = ""):
        self.ram = ram
        self.ssd = ssd

    def __str__(self):
        return "MacBookSystem(ram={}, ssd={})".format(
            self.ram, self.ssd
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            'ram': self.ram,
            'ssd': self.ssd
        }

    @staticmethod
    def from_dict(d) -> 'MacBookSystemVO':
        try:
            return MacBookSystemVO(
                ram=d['ram'],
                ssd=d['ssd']
            )
        except KeyError as e:
            return MacBookSystemVO()
