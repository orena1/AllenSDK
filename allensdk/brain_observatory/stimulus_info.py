# some handles for stimulus types
DRIFTING_GRATINGS = 'drifting_gratings'
STATIC_GRATINGS = 'static_gratings'
NATURAL_MOVIE_ONE = 'natural_movie_one'
NATURAL_MOVIE_TWO = 'natural_movie_two'
NATURAL_MOVIE_THREE = 'natural_movie_three'
NATURAL_SCENES = 'natural_scenes'
LOCALLY_SPARSE_NOISE = 'locally_sparse_noise'
SPONTANEOUS_ACTIVITY = 'spontaneous'

# handles for stimulus names
THREE_SESSION_A = 'three_session_A'
THREE_SESSION_B = 'three_session_B'
THREE_SESSION_C = 'three_session_C'

SESSION_STIMULUS_MAP = {
    THREE_SESSION_A: [ DRIFTING_GRATINGS, NATURAL_MOVIE_ONE, NATURAL_MOVIE_THREE, SPONTANEOUS_ACTIVITY ],
    THREE_SESSION_B: [ STATIC_GRATINGS, NATURAL_SCENES, NATURAL_MOVIE_ONE, SPONTANEOUS_ACTIVITY ],
    THREE_SESSION_C: [ LOCALLY_SPARSE_NOISE, NATURAL_MOVIE_ONE, NATURAL_MOVIE_TWO, SPONTANEOUS_ACTIVITY ]
    }

def stimuli_in_session(session):
    """ Return a list what stimuli are available in a given session. 
    
    Parameters
    ----------
    session: string
        Must be one of: [stimulus_info.THREE_SESSION_A, stimulus_info.THREE_SESSION_B, stimulus_info.THREE_SESSION_C]
    """
    return SESSION_STIMULUS_MAP[session]
