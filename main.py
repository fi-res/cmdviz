from os import get_terminal_size
from typing import TYPE_CHECKING, cast

from numpy import abs, hanning, log10, logspace, mean, ndarray, where
from numpy.fft import rfft, rfftfreq
from soundcard import default_microphone, default_speaker, get_microphone

if TYPE_CHECKING:
    from soundcard import _Microphone, _Recorder


USE_MIC = False
MIN_HZ = 15
MAX_HZ = 16000
BANDS_LOGARIPHMIC = False
BLOCKSIZE = 1500
SAMPLERATE = 44100
MAX_VOLUME = 100


def draw(volume: float):
    volume = min(volume, MAX_VOLUME) / MAX_VOLUME * width
    v = str(round(volume, 1))
    # color = "37"
    # if volume > 60:
    #     color = "31"
    # elif volume > 40:
    #     color = "33"
    # elif volume > 20:
    #     color = "32"
    # elif volume > 10:
    #     color = "36"
    # return f"{v}{' ' * (6 - len(v))}\033[{round(volume)}m{'&' * min(width - 6, round(volume))}\033[0m"
    return f"{v}{' ' * (6 - len(v))}{'&' * round(volume)}"


height = get_terminal_size().lines - 3
width = get_terminal_size().columns - 10

if BANDS_LOGARIPHMIC:
    _edges = logspace(log10(MIN_HZ), log10(MAX_HZ), height + 1)
    bands = [(_edges[i], _edges[i + 1]) for i in range(height)]
else:
    _edges = list(range(MIN_HZ, MAX_HZ, MAX_HZ // height))
    bands = [(_edges[i], _edges[i + 1]) for i in range(height - 1)]

print("\n" * height)

device: _Microphone = get_microphone(
    (default_microphone() if USE_MIC else default_speaker()).name,
    include_loopback=not USE_MIC
)
with device.recorder(SAMPLERATE, blocksize=BLOCKSIZE) as recorder:
    if TYPE_CHECKING:
        recorder = cast(_Recorder, recorder)

    while True:
        data: ndarray = recorder.record().mean(axis=1)

        freqs = rfftfreq(len(data), 1 / SAMPLERATE)
        mags = abs(rfft(data * hanning(len(data))))

        volumes = []
        for _min, _max in bands:
            idx = where((freqs >= _min) & (freqs <= _max))[0]
            # print(mags[idx])
            volumes.append(mean(mags[idx]) if len(idx) > 0 else 0)

        print(
            f"\033[{height}A{''.join([f'\033[K{draw(volume)}\n' for volume in volumes])}"
        )
