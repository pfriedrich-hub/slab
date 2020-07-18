'''
Michaela's experiment:
Interference between room and voice processing
Use like this:
>>> from slab.experiments import room_voice_interference
>>> room_voice_interference('subject01')
'''

import time
import functools
import pathlib
import os
import collections
import numpy
import scipy
import slab

# confiuration
# could go into config file and be loaded here with cfg = slab.load_config('config.txt'),
# then variables are accessible as cfg.speaker_positions etc.
slab.Signal.set_default_samplerate(44100)
_results_file = None
slab.Resultsfile.results_folder = 'Results'
# possible parameters:
rooms = tuple(range(40, 161, 8)) # (40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160)
voices = (0.98, 1.029, 1.078, 1.127, 1.176, 1.225, 1.274, 1.323, 1.372, 1.421, 1.47)
itds = tuple(range(0, 401, 40)) # (0, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400)
default_room = rooms[0] # 40
default_voice = voices[0] # 0.98
default_itd = itds[0] # 0
ISI_stairs = 0.15
_after_stim_pause = 0.3
#word_list = ['Aertel', 'Apor', 'Aucke', 'Bohke', 'Dercke', 'Eika', 'Eukof', 'Felcke', 'Geke', 'Gelkat', 'Kansup', 'Kelpeit', 'Kirpe', 'Kitlu', 'Klamsup', 'Kontus', 'Lanrapf', 'Manzeb', 'Nukal', 'Pekus', 'Perkus', 'Raupfan', 'Reiwat', 'Repad', 'Retel', 'Schaujak', 'Seckuck', 'Sekaak', 'Stiecke', 'Subter', 'Trepfel', 'Tunsat', 'Verzung', 'Waatep', 'Wieken', 'Zeten']
word_list = ['Aertel', 'Apor', 'Aucke']
# folder 'stimuli' in same folder as the script:
#stim_folder = pathlib.Path(__file__).parent.resolve() / pathlib.Path('Stimuli')
stim_folder = pathlib.Path('/Users/Marc/Documents/Projects') / pathlib.Path('Stimuli')
condition = collections.namedtuple('condition', ['voice', 'room', 'itd', 'label']) # used to set parameters in interference_block

def jnd(condition, practise=False):
    '''
    Presents a staricase for a 2AFC task and returns the threshold.
    This threshold is used in the main experiment as jnd.
    condition ... 'room', voice', or 'itd'
    '''
    print('Two sounds are presented in each trial.')
    print('They are always different, but sometimes')
    if condition == 'room':
        print('they are played in two rooms with different sizes,')
        print('and sometimes both are played in the same room.')
        print('Was the larger room presented first or second?')
    elif condition == 'voice':
        print('they are spoken by two different persons (one larger, one smaller),')
        print('and sometimes both are spoken by the same person.')
        print('Was the larger person presented first or second?')
    elif condition == 'itd':
        print('they are played from two different directions (one slightly to the left),')
        print('and sometimes both are played from straight ahead.')
        print('Was the sound slightly from the left played first or second?')
    else:
        raise ValueError(f'Invalid condition {condition}.')
    print('Press 1 for first, 2 for second.')
    print('The difference will get more and more difficult to hear.')
    input('Press enter to start JND estimation...')
    repeat = 'r'
    condition_values = globals()[condition+'s'] # get the parameter list (vars rooms, voices, or itds) from condition string
    while repeat == 'r':
        # make a random, non-repeating list of words to present during the staircase
        word_seq = slab.Trialsequence(conditions=word_list, kind='infinite', name='word_seq')
        # define the staircase
        if practise:
            stairs = slab.Staircase(start_val=len(condition_values)-1, n_reversals=5,
                                step_sizes=[4, 4, 3, 2], min_val=0, max_val=len(condition_values)-1, n_up=1, n_down=1, n_pretrials=0)
        else:
            stairs = slab.Staircase(start_val=len(condition_values)-4, n_reversals=12,
                                step_sizes=[3, 2, 1], min_val=0, max_val=len(condition_values)-1, n_up=1, n_down=1, n_pretrials=2)
            _results_file.write(f'{condition} jnd:', tag='time')
        for trial in stairs:
            current = condition_values[trial]
            # load stimuli
            word = next(word_seq)
            word2 = next(word_seq)
            if condition == 'room':
                jnd_stim = slab.Sound(stim_folder / word  / f'{word}_SER{default_voice:.4g}_GPR168_{current}_{default_itd}.wav')
            elif condition == 'voice':
                jnd_stim = slab.Sound(stim_folder / word  / f'{word}_SER{current:.4g}_GPR168_{default_room}_{default_itd}.wav')
            elif condition == 'itd':
                jnd_stim = slab.Sound(stim_folder / word  / f'{word}_SER{default_voice:.4g}_GPR168_{default_room}_{current}.wav')
            default_stim = slab.Sound(stim_folder / word2 / f'{word2}_SER{default_voice:.4g}_GPR168_{default_room}_{default_itd}.wav')
            stairs.present_afc_trial(jnd_stim, default_stim, isi=ISI_stairs)
            if practise:
                stairs.plot()
        thresh = stairs.threshold(n=6)
        thresh_condition_value = condition_values[numpy.ceil(thresh).astype('int')]
        if practise:
            stairs.close_plot()
        else:
            # TODO: save staircase as json string into results file
            print(f'room jnd: {round(thresh, ndigits=1)}')
            _results_file.write(thresh, tag=f'jnd {condition}')
            _results_file.write(thresh_condition_value, tag=f'jnd condition value {condition}')
        repeat = input('Press enter to continue, "r" to repeat this threshold measurement.\n\n')
    return thresh_condition_value

# same-diff task, method of constant stimuli, 5 conditions, 40 reps (20 diff, 20 same)
def interference_block(jnd_room, jnd_voice, jnd_itd):
    '''
    Presents one condition block of the the interference test.
    Condition ... 'room', 'room+voice', 'room+itd', 'voice', or 'itd'
    default_room etc. ... the reference room, SER and ITD values.
    jnd_room etc. ... the room, SER and ITD values that are perceived as different from the default
                      (default value + measured jnd rounded to the nearest available stimulus)
    '''
    print('Two sounds are presented in each trial.')
    print('They are always different, but sometimes')
    print('they are played in two rooms with different sizes,')
    print('and sometimes both are played in the same room.')
    print('Was the larger room presented first or second?')
    print('Press 1 for first, 2 for second.')
    input('Press enter to start the test...')
    # set parameter values of conditions in named tuples -> list of these is used for slab.Trialsequence
    default = condition(voice=default_voice, room=default_room, itd=default_itd, label='default')
    room = condition(voice=default_voice, room=jnd_room, itd=default_itd, label='room')
    room_voice = condition(voice=jnd_voice, room=jnd_room, itd=default_itd, label='room_voice')
    room_itd = condition(voice=default_voice, room=jnd_room, itd=jnd_itd, label='room_itd')
    voice = condition(voice=jnd_voice, room=default_room, itd=default_itd, label='voice')
    itd = condition(voice=default_voice, room=default_room, itd=jnd_itd, label='itd')
    conditions = [default, room, room_voice, room_itd, voice, itd]
    trials = slab.Trialsequence(conditions=conditions, n_reps=10, kind='random_permutation')
    word_seq = slab.Trialsequence(conditions=word_list, kind='infinite', name='word_seq')
    hits = 0
    false_alarms = 0
    _results_file.write(f'interference block:', tag='time')
    for trial_parameters in trials:
        # load stimuli
        word = next(word_seq)
        word2 = next(word_seq)
        jnd_stim = slab.Sound(stim_folder / word  / word+'_SER%.4g_GPR168_%i_%i.wav' % trial_parameters)
        default_stim = slab.Sound(stim_folder / word2 / word2+'_SER%.4g_GPR168_%i_%i.wav' % default)
        trials.present_afc_trial(jnd_stim, default_stim, isi=ISI_stairs)
        response = trials.data[-1] # read out the last response
        if trial_parameters.label[:4] == 'room' and response: # hit!
            hits += 1
        elif trial_parameters.label[:4] != 'room' and response: # false alarm!
            false_alarms += 1
        time.sleep(_after_stim_pause)
    hitrate = hits/trials.n_trials
    print(f'hitrate: {hitrate}')
    farate = false_alarms/trials.n_trials
    print(f'false alarm rate: {farate}')
    _results_file.write(trials, tag='trials')

def main_experiment(subject=None):
    global _results_file
    # set up the results file
    if not subject:
        subject = input('Enter subject code: ')
    _results_file = slab.Resultsfile(subject=subject)
    # _ = familiarization() # run the familiarization, the hitrate is saved in the results file
    jnd('room', practise=True)  # run the stairs practice for the room condition
    jnd_room = jnd('room') # mesure
    jnd('voice', practise=True)  # run the stairs practice for the room condition
    jnd_voice = jnd('voice')
    jnd('itd', practise=True)  # run the stairs practice for the room condition
    jnd_itd = jnd('itd')

    print('The main part of the experiment starts now (interference task).')
    print('Blocks of about 4min each are presented with pauses inbetween.')
    for _ in range(10):
        interference_block(jnd_room, jnd_voice, jnd_itd)

if __name__ == '__main__':
    main_experiment()