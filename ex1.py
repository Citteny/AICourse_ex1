def parsefile(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        algorithm_num = int(lines[0])
        size = int(lines[1])
        state_as_list = [int(num) for num in lines[2].split('-')]
    return algorithm_num, size, state_as_list


class TilePuzzleLogic:
    def __init__(self, size, goal_state):
        self.size = size
        self.goal_state = goal_state
        self.length = self.size ** 2

    def get_successors(self, tile_puzzle_node):
        successors = []
        empty_tile_index = tile_puzzle_node.state.state_list.index(0)

        # Up
        if empty_tile_index + self.size < self.length:
            state_list_copy = list(tile_puzzle_node.state.state_list)
            self._swap(state_list_copy, empty_tile_index, empty_tile_index + self.size)
            successors.append(Node(tile_puzzle_node, TilePuzzleState(state_list_copy, 'U')))

        # Down
        if empty_tile_index - self.size >= 0:
            state_list_copy = list(tile_puzzle_node.state.state_list)
            self._swap(state_list_copy, empty_tile_index, empty_tile_index - self.size)
            successors.append(Node(tile_puzzle_node, TilePuzzleState(state_list_copy, 'D')))

        # Left
        if empty_tile_index % self.size < self.size - 1:
            state_list_copy = list(tile_puzzle_node.state.state_list)
            self._swap(state_list_copy, empty_tile_index, empty_tile_index + 1)
            successors.append(Node(tile_puzzle_node, TilePuzzleState(state_list_copy, 'L')))

        # Right
        if empty_tile_index % self.size > 0:
            state_list_copy = list(tile_puzzle_node.state.state_list)
            self._swap(state_list_copy, empty_tile_index, empty_tile_index - 1)
            successors.append(Node(tile_puzzle_node, TilePuzzleState(state_list_copy, 'R')))

        return successors

    @staticmethod
    def _swap(list, i, j):
        list[i], list[j] = list[j], list[i]

    def list_index_to_matrix_indices(self, list_index):
        row_index = int(list_index / self.size)
        column_index = list_index % self.size
        return row_index, column_index


class TilePuzzleState:
    def __init__(self, state, operation):
        self.state_list = state
        self.operation = operation

    def __hash__(self):
        return hash(str(self.state_list))

    def __repr__(self):
        return str(self.state_list)


class Node:
    def __init__(self, parent, state):
        self.state = state
        self.parent = parent

    def get_path_from_root(self):
        current = self
        path = []
        while current.parent:
            path.append(current.state.operation)
            current = current.parent
        path.reverse()
        return ''.join(path)

    def __hash__(self):
        return hash(self.state)

    def __repr__(self):
        return str(self.state)

    def __lt__(self, other):
        return False


class Algorithms:
    def __init__(self, init_node, game_logic):
        self.init_state = init_node
        self.game_logic = game_logic
        self._algorithms = {1: ('IDS', self._ids), 2: ('BFS', self._bfs), 3: ('A*', self._a_star)}

    def _bfs(self):
        from collections import deque
        queue = deque([self.init_state])
        counter = 0
        while queue:
            current_node = queue.popleft()
            counter += 1
            if self.game_logic.goal_state == current_node.state.state_list:
                path = current_node.get_path_from_root()
                return path, str(counter), 0
            queue.extend(self.game_logic.get_successors(current_node))
        return 'No Solution', counter, 0

    def _ids(self):
        depth = 0
        while True:
            node, count = self._ids_loop(self.init_state, depth)
            if node:
                path = node.get_path_from_root()
                return path, count, depth
            depth += 1

    def _ids_loop(self, node_current, depth):
        if node_current.state.state_list == self.game_logic.goal_state:
            return node_current, 1
        if depth == 0:
            return None, 1
        counter = 1
        successors = self.game_logic.get_successors(node_current)
        for node_succ in successors:
            solution, opened = self._ids_loop(node_succ, depth - 1)
            counter += opened
            if solution:
                return solution, counter
        return None, counter

    def _a_star(self):
        from heapq import heappop, heappush
        game_logic = self.game_logic
        init_node = self.init_state
        priority_queue = []
        g_func_dict = {init_node: 0}
        heappush(priority_queue, (g_func_dict[init_node] + self.manhattan_distance(init_node, game_logic), init_node))
        # c = set()
        counter = 0
        while priority_queue:
            f_of_node, node = heappop(priority_queue)
            counter += 1
            if node.state.state_list == game_logic.goal_state:
                path = node.get_path_from_root()
                return path, str(counter), g_func_dict[node]
            # if node in c:
            #     continue
            # c.add(node)
            successors = game_logic.get_successors(node)
            for succ_node in successors:
                g_func_dict[succ_node] = g_func_dict[node] + 1
                heappush(priority_queue,
                         (g_func_dict[succ_node] + self.manhattan_distance(succ_node, game_logic), succ_node))

    @staticmethod
    def manhattan_distance(node, game_logic):  # the h func
        sum = 0
        for i, n in enumerate(node.state.state_list):
            if n == 0:
                continue
            else:
                this_x, this_y = game_logic.list_index_to_matrix_indices(i)
                goal_x, goal_y = game_logic.list_index_to_matrix_indices(game_logic.goal_state.index(n))
                sum += abs(this_x - goal_x) + abs(this_y - goal_y)
        return sum

    def solve(self, algorithm_number):
        return self._algorithms[algorithm_number][1]()


if __name__ == '__main__':
    algo_num, board_size, initial_state_list = parsefile('files/input.txt')
    length = board_size ** 2
    goal_state = [n % length for n in range(1, length + 1)]
    initial_node = Node(None, TilePuzzleState(initial_state_list, None))
    algorithms = Algorithms(initial_node, TilePuzzleLogic(board_size, goal_state))
    path_from, num_opened, depth_from = algorithms.solve(algo_num)
    print(path_from + ' ' + str(num_opened) + ' ' + str(depth_from))
    with open('output.txt', 'w') as f:
        f.writelines(path_from + ' ' + str(num_opened) + ' ' + str(depth_from))
