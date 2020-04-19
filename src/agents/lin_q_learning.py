import numpy as np
from tile_coding import *

class LinQLearningAgent:
    """
    Initialization of Sarsa Agent. All values are set to None so they can
    be initialized in the agent_init method.
    """
    def __init__(self, agent_init_info):
        """Setup for the agent called when the experiment first starts."""
        self.num_tilings = agent_init_info["num_tilings"]
        self.num_tiles = agent_init_info["num_tiles"]
        self.state_ranges = agent_init_info["state_ranges"]
        self.epsilon = agent_init_info["epsilon"]
        self.discount = agent_init_info["discount"]
        self.step_size = agent_init_info["step_size"] / self.num_tilings
        self.num_actions = agent_init_info.get("num_actions", None)

        self.state_dim = len(self.state_ranges[0])
        self.feature_dim = self.num_tilings * (self.num_tiles ** self.state_dim)
        self.initial_weights = agent_init_info.get("initial_weights", np.zeros((self.num_actions, self.feature_dim)))
        self.w = np.ones((self.num_actions, self.feature_dim)) * self.initial_weights

        self.tc = TileCoder(self.num_tilings, self.num_tiles, self.state_ranges)

    def select_action(self, tiles):
        """
        Selects an action using epsilon greedy
        Args:
        tiles - np.array, an array of active tiles
        Returns:
        (chosen_action, action_value) - (int, float), tuple of the chosen action
                                        and it's value
        """
        action_values = []
        chosen_action = None

        action_values = self.w[:, tiles].sum(axis=1)
        epsilon = np.random.random()
        if epsilon < self.epsilon:
            chosen_action = np.random.randint(0, self.num_actions -1)
        else:
            chosen_action = self.argmax(action_values)

        return chosen_action, action_values

    def agent_start(self, state):
        """The first method called when the experiment starts, called after
        the environment starts.
        Args:
            state (Numpy array): the state observation from the
                environment's evn_start function.
        Returns:
            The first action the agent takes.
        """
        active_tiles = self.tc.get_features(state)
        current_action = self.select_action(active_tiles)[0]

        self.last_action = current_action
        self.previous_tiles = np.copy(active_tiles)
        return self.last_action

    def agent_step(self, reward, state):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            state (Numpy array): the state observation from the
                environment's step based, where the agent ended up after the
                last step
        Returns:
            The action the agent is taking.
        """

        active_tiles = self.tc.get_features(state)
        current_action, current_q = self.select_action(active_tiles)

        max_q = np.max(current_q)
        target = reward + self.discount * max_q
        obs = self.w[:, self.previous_tiles].sum(axis=1)[self.last_action]

        self.w[self.last_action,self.previous_tiles] += self.step_size * (target - obs)

        self.last_action = current_action
        self.previous_tiles = np.copy(active_tiles)
        return self.last_action

    def agent_end(self, reward):
        """Run when the agent terminates.
        Args:
            reward (float): the reward the agent received for entering the
                terminal state.
        """

        target = reward
        obs = self.w[:, self.previous_tiles].sum(axis=1)[self.last_action]

        self.w[self.last_action,self.previous_tiles] += self.step_size * (target - obs)

    def argmax(self, q_values):
        """argmax with random tie-breaking
        Args:
            q_values (Numpy array): the array of action-values
        Returns:
            action (int): an action with the highest value
        """
        top = float("-inf")
        ties = []

        for i in range(len(q_values)):
            if q_values[i] > top:
                top = q_values[i]
                ties = []

            if q_values[i] == top:
                ties.append(i)

        return np.random.choice(ties)

    def greedy_policy(self, state):
        ft = self.tc.get_features(state)
        return self.argmax(self.w[:, ft].sum(axis=1))
