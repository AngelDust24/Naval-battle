from random import randint


# Общий класс исключений доски
class BoardException(Exception):
    pass


# Ошибка выстрел за доску
class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за доску!"


# Ошибка дублированный выстрел
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы стреляли в эту точку"


# Ошибка неразрешенное расположение корабля
class BoardWrongShipException(BoardException):
    pass


class Dot:
    # Проверка параметра на пренадлежность к типу int
    @classmethod
    def __type_checking_int(cls, value):
        if type(value) is not int:
            raise TypeError("Ожидается int")

    def __init__(self, x, y):
        self.__type_checking_int(x)
        self.__x = x
        self.__type_checking_int(y)
        self.__y = y

    def __eq__(self, other):
        return self.__x == other.x and self.__y == other.y

    def __add__(self, other):
        return Dot(self.__x + other.x, self.__y + other.y)

    def __repr__(self):
        return f'Dot(x:{self.__x}, y:{self.__y})'

    # Оставляем __x только для чтения
    @property
    def x(self):
        return self.__x

    # Оставляем __y только для чтения
    @property
    def y(self):
        return self.__y


class Ship:
    # Проверка параметра на пренадлежность к типу Dot
    @classmethod
    def __type_checking_dot(cls, value):
        if type(value) is not Dot:
            raise TypeError("Ожидается Dot")

    # Расчет ХП корабля
    @classmethod
    def __calculation_hitpoints(cls, bow, stern):
        if bow.x == stern.x:
            return stern.y - bow.y + 1
        else:
            return stern.x - bow.x + 1

    def __init__(self, bow, stern):
        # Координаты носа корабля
        self.__type_checking_dot(bow)
        self.__bow = bow
        # Координаты кормы корабля
        self.__type_checking_dot(stern)
        self.__stern = stern
        # Очки жизней корабля
        self.__hitpoints = self.__calculation_hitpoints(bow, stern)

    # Возращает корабль в виде списка точек
    @property
    def dots(self):
        ship_dots = []
        # Если точки x в начале и конце равны изменяются только точки y
        if self.__bow.x == self.__stern.x:
            for y in range(self.__bow.y, self.__stern.y + 1):
                ship_dots.append(Dot(self.__bow.x, y))
        # Иначе изменяются только точки x
        else:
            for x in range(self.__bow.x, self.__stern.x + 1):
                ship_dots.append(Dot(x, self.__stern.y))
        return ship_dots

    @property
    def hitpoints(self):
        return self.__hitpoints

    @hitpoints.setter
    def hitpoints(self, value):
        self.__hitpoints = value


class PlayingField:
    # Проверка параметра на пренадлежность к типу int
    @classmethod
    def __type_checking_int(cls, size):
        if type(size) is not int:
            raise TypeError("Ожидается int")

    # Проверка параметра на пренадлежность к типу bool
    @classmethod
    def __type_checking_bool(cls, hide):
        if type(hide) is not bool:
            raise TypeError("Ожидается bool")

    def __init__(self, size=6, hide=False):
        self.__type_checking_int(size)
        self.__size = size
        self.__type_checking_bool(hide)
        self.__hide = hide
        self.__field = [['O'] * size for _ in range(size)]
        self.__list_ship = []
        self.__busy_dots = []
        self.__count = 0

    def __str__(self):
        field = "  | 1 | 2 | 3 | 4 | 5 | 6 | X\n"
        for i, row in enumerate(self.__field):
            field += f"{i + 1} | " + ' | '.join(row) + ' |\n'
        # Если спрятать истинно заменяем символы
        if self.__hide:
            field = field.replace('■', 'O')
        return field + 'Y'

    # Проверка лежит ли точка за пределами поля
    def out(self, dot):
        return not (0 <= dot.x < self.__size and 0 <= dot.y < self.__size)

    # Добавляет контур корабля в список занятых точек при необходимости отражает контур на поле
    def contour(self, ship, hide=False):
        # Точки прилегающие к центральной
        adjacent_dots = [(-1, 1), (0, 1), (1, 1),
                         (-1, 0), (0, 0), (1, 0),
                         (-1, -1), (0, -1), (1, -1)]
        for ship_dot in ship.dots:
            for dot_x, dot_y in adjacent_dots:
                current_dot = Dot(ship_dot.x + dot_x, ship_dot.y + dot_y)
                # Проверка есть ли точка в списке занятых точек и не выходит ли за граници поля
                if current_dot is not self.__busy_dots and not self.out(current_dot):
                    # Если отображение разрешено отобразить точки на поле
                    if hide:
                        self.__field[current_dot.y][current_dot.x] = '-'
                    # Добавление точек в список занятых точек
                    self.__busy_dots.append(current_dot)

    # Добавляет корабль на доску
    def add_ship(self, ship):
        for ship_dot in ship.dots:
            if self.out(ship_dot) or ship_dot in self.__busy_dots:
                raise BoardWrongShipException
        for ship_dot in ship.dots:
            self.__field[ship_dot.y][ship_dot.x] = '■'
            self.__busy_dots.append(ship_dot)
        self.__list_ship.append(ship)
        self.contour(ship)

    # Выстрел по кораблю
    def shot(self, dot):
        # Выстрел за доску
        if self.out(dot):
            raise BoardOutException
        # Выстрел в запрещенную точку
        if dot in self.__busy_dots:
            raise BoardUsedException
        self.__busy_dots.append(dot)
        for ship in self.__list_ship:
            # Проверка попадания по кораблю
            if dot in ship.dots:
                ship.hitpoints -= 1
                self.__field[dot.y][dot.x] = 'X'
                # Если hitpoints равен нулю корабль уничтожен
                if ship.hitpoints == 0:
                    self.__count += 1
                    self.contour(ship, hide=True)
                    print("Корабль уничтожен")
                    return False
                # Иначе корабль ранен
                else:
                    print("Корабль ранен")
                    return True
            self.__field[dot.y][dot.x] = '-'
            print("Мимо")
            return False

    # Устанавливает пустой список занятых точек
    def begin(self):
        self.__busy_dots = []

    # Если кол-во уничтоженных кораблей равно кол-ву кораблей на доске то поражение
    def defeat(self):
        return self.__count == len(self.__list_ship)

    @property
    def hide(self):
        return self.__hide

    @hide.setter
    def hide(self, hide):
        self.__hide = hide


class Player:
    # Проверка параметра на принадлежность к типу PlayingField
    @classmethod
    def __type_checking_playing_field(cls, board):
        if type(board) is not PlayingField:
            raise TypeError("Ожидается PlayingField")

    def __init__(self, board, enemy):
        self.__type_checking_playing_field(board)
        self.board = board
        self.__type_checking_playing_field(enemy)
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    # Делаем выстрел
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as exception:
                print(exception)


class AI(Player):
    # Ход ИИ
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    # Ход игрока
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.__size = size
        player = self.random_field()
        ordenador = self.random_field()
        # Скрываем корабли для ИИ
        ordenador.hide = True
        self.__ai = AI(ordenador, player)
        self.__user = User(player, ordenador)

    # Приветствие пользователя
    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    # Генерация кординат корабля
    @classmethod
    def __ship_generation(cls, len_ship, size_field):
        if len_ship == 1:
            bow = Dot(randint(0, size_field), randint(0, size_field))
            return Ship(bow, bow)
        else:
            orientation = [Dot(0, len_ship - 1), Dot(len_ship - 1, 0)]
            bow = Dot(randint(0, size_field), randint(0, size_field))
            stern = bow + orientation[randint(0, 1)]
            return Ship(bow, stern)

    # Создание доски со случайным расположением кораблей до 1000 итераций
    def create_field(self):
        # Список длин кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = PlayingField(size=self.__size)
        # Попытки создать поле
        attempts = 0
        for len_ship in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = self.__ship_generation(len_ship, self.__size)
                # Ловим исключение ошибка постановки корабля
                try:
                    field.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        field.begin()
        return field

    # Гарантированное создание случайной доски
    def random_field(self):
        field = None
        while field is None:
            field = self.create_field()
        return field

    # Игровой цикл
    def game_cycle(self):
        stroke_number = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.__user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.__ai.board)
            print("-" * 20)
            if stroke_number % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.__user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.__ai.move()
            if repeat:
                stroke_number -= 1

            if self.__ai.board.defeat():
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.__user.board.defeat():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            stroke_number += 1

    def start(self):
        self.greet()
        self.game_cycle()


g = Game()
g.start()
