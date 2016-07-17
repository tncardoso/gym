import numpy as np
from grpc.beta import implementations
import qwop_pb2

import gym
from gym import spaces
from gym.utils import seeding

PIXELS=128

ACTION_MEANING = {
    0: 'Q',
    1: 'W',
    2: 'O',
    3: 'P',
    4: 'QW',
    5: 'QO',
    6: 'QP',
    7: 'WO',
    8: 'WP',
    9: 'OP',
    10: 'QWO',
    11: 'QWP',
    12: 'QOP',
    13: 'WOP',
    14: 'QWOP',
    15: 'NTHING',
}

class QwopEnv(gym.Env):
    """
    QWOP Environment

    Learning how to run in QWOP.
    """

    def __init__(self):
        self._seed()

        self._width = 80
        self._height = 50
        self.action_space = spaces.Discrete(len(ACTION_MEANING))
        self.observation_space = spaces.Box(low=0, high=255,
                shape=(self._height, self._width))

        self._channel = implementations.insecure_channel('localhost', 1212)
        self._stub = qwop_pb2.beta_create_QwopServer_stub(self._channel)
        self._timeout = 50

        self._reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _destroy(self):
        pass

    def _reset(self):
        self._score = 0.0
        keys = qwop_pb2.Keys(r=True)
        self._stub.Click(keys, self._timeout)

    def _click(self, code):
        meaning = ACTION_MEANING[code]
        q, w, o, p = (False, False, False, False)
        if 'Q' in meaning: q = True
        if 'W' in meaning: w = True
        if 'O' in meaning: o = True
        if 'P' in meaning: p = True
        keys = qwop_pb2.Keys(q=q, w=w, o=o, p=p)
        self._stub.Click(keys, self._timeout)

    def _get_score(self):
        return self._stub.GetScore(qwop_pb2.Empty(), self._timeout).score

    def _get_obs(self):
        '''Get observable space'''
        screen = self._stub.GetScreen(qwop_pb2.Empty(), self._timeout)
        arr = np.zeros((screen.height, screen.width), dtype=np.uint8)
        for y in range(screen.height):
            for x in range(screen.width):
                ix = (y * screen.width) + x
                arr[y,x] = screen.pixels[ix]
        return (arr, screen.finished)

    def _step(self, action):
        reward = 0.0
        num_steps = self.np_random.randint(2, 5)
        for _ in range(num_steps):
            self._click(action)
            new_score = self._get_score()
            reward += new_score - self._score
            self._score = new_score
        (ob, is_over) = self._get_obs()

        return ob, reward, is_over, {}

if __name__ == '__main__':
    env = QwopEnv()
    env._get_obs()
    #resp = stub.GetScore(qwop_pb2.Empty(), 10)
    #print(resp)
    #resp = stub.GetScreen(qwop_pb2.Empty(), 10)
    #print(resp.width)
    #print(resp.height)
    #print(len(resp.pixels))

