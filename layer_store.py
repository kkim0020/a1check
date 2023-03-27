from __future__ import annotations
from abc import ABC, abstractmethod
from layer_util import Layer
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from layer_util import get_layers
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem

class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass

class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """

    def __init__(self):
        self.layer: Layer = None
        self.set_invert = False


    def add(self, layer: Layer) -> bool:

        self.layer = layer
        return True

    def erase(self, layer: Layer) -> bool:
        '''set layer to None'''
        self.layer = None
        return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:

        if self.layer is None:
            return start
        if self.set_invert:
            color = self.layer.apply(start, timestamp, x, y)
            color = (255 - color[0], 255 - color[1], 255 - color[2])
        else:
            color = self.layer.apply(start, timestamp, x, y)
        return color

    def special(self):
        ''' invert get_color output'''

        self.set_invert = not self.set_invert



class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """
    layer_count = len(get_layers())

    def __init__(self):
        self.layers = CircularQueue(self.layer_count * 100)

    def add(self, layer: Layer) -> bool:
        self.layers.append(layer)
        return True

    def erase(self, layer: Layer) -> bool:
        erased_layer = self.layers.serve()
        if erased_layer:
            return True
        return False

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:

        color = start

        front = self.layers.front
        length = self.layers.length

        while True:
            try:
                layer = self.layers.serve()
                color = layer.apply(color, timestamp, x, y)
            except:
                break

        self.layers.front = front
        self.layers.length = length
        return color

    def special(self):

        new_stack = ArrayStack(self.layer_count * 100)
        new_queue = CircularQueue(self.layer_count * 100)

        for _ in range(len(self.layers)):
            new_stack.push(self.layers.serve())

        for _ in range(len(new_stack)):
            new_queue.append(new_stack.pop())

        self.layers = new_queue


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """
    layer_count = len(get_layers())

    def __init__(self):
        self.layers = ArraySortedList(self.layer_count)

    def add(self, layer: Layer) -> bool:
        '''ArraySortedList의 __contains__이용하여 이미 있는지 확인 후 add'''
        if ListItem(layer, layer.index) in self.layers:
            return False
        else:
            self.layers.add(ListItem(layer, layer.index))
            return True

    def erase(self, layer: Layer) -> bool:
        # 둘중 하나를 선택하세요
        '''# __conatins__를 활용한 if else 구문
        if ListItem(layer, layer.index) not in self.layers:
            return False
        else:
            index = self.layers.index(ListItem(layer, layer.index))
            delete_layer = self.layers.delete_at_index(index)
            return True'''
        # index 함수의 error 를 이용한 try except 구문
        try:
            index = self.layers.index(ListItem(layer, layer.index))
            delete_layer = self.layers.delete_at_index(index)
            return True
        except:
            return False

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        color = start
        # 기존 문제를 두고 푸는 방법
        length = self.layers.length
        for i in range(length):
            list_item = self.layers[i]
            color = list_item.value.apply(color, timestamp, x, y)
        return color

    def special(self):
        ''' find median value in lexicographical order and set it un-applying'''
        lexicographic_order_sorted_list = ArraySortedList(self.layer_count)

        ''' 
        layer name을 꺼내서 ord 함수로 key를 생성해서 
        lexicographic_order_sorted_list 생성
        layer의 앞 두자리까지 확인해야 layer들의 순서를 확인할 수 있기 때문에
        ord(a) = 97 ord(z) = 122
        order index는 첫째글자ord * 1000 + 둘째글자ord  
        '''
        length = self.layers.length

        if length == 0:
            return

        for i in range(length):
            list_item = self.layers[i]
            layer = list_item.value
            name = layer.name
            order_index = ord(name[0]) * 1000 + ord(name[1])
            lexicographic_order_sorted_list.add(ListItem(layer, order_index))

        '''
        짝수면 중간값중 앞의 값
        홀수면 중간값
        '''
        length = lexicographic_order_sorted_list.length
        if length % 2 == 0:
            '''if length = 6 get 2(index)'''
            mid = (length / 2) - 1
        else:
            '''if length = 5 get 2(index)'''
            mid = (length // 2)

        counter = 0
        layer_to_erase: Layer = None
        for list_item in lexicographic_order_sorted_list.array:
            if list_item is None:
                continue
            if mid == counter:
                layer_to_erase = list_item.value
                break
            counter += 1
        # 둘중에 하나를 골라서 선택하세요.
        # erase 구현
        '''
        index_to_erase = self.layers.index(ListItem(layer_to_erase, layer_to_erase.index))
        self.layers.delete_at_index(index_to_erase)
        '''

        # self.erase활용
        self.erase(layer_to_erase)