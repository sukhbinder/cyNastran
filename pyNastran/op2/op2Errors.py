class InvalidCodeError(RuntimeError):
    pass

class InvalidAnalysisCodeError(InvalidCodeError):
    pass

class InvalidATFSCodeError(InvalidCodeError):
    pass

class InvalidFormatCodeError(InvalidCodeError):
    pass


class InvalidGridID_Error(ValueError):
    pass

class AddNewElementError(InvalidCodeError):
    pass

class EndOfFileError(RuntimeError):
    pass

class TapeCodeError(RuntimeError):
    pass

class ZeroBufferError(RuntimeError):
    pass

class InvalidMarkersError(RuntimeError):
    pass

class InvalidMarkerError(RuntimeError):
    pass
