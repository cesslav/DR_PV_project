import sqlite3


class DBClass:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def add_to_leaderboard(self, time, diamonds_collected, user_name="John Doe"):
        lead_id = self.cursor.execute("""
            SELECT ID
            FROM leaders
            """).fetchall()
        max_id = []
        for i in lead_id:
            max_id.append(i[0])
        max_id = max(max_id) + 1
        self.cursor.execute("""
            INSERT INTO Leaders
            VALUES (?,?,?,?,?)
            """, (max_id, user_name,
                  str(datetime.now())[11:16],
                  time, diamonds_collected))
        self.connection.commit()
        log_file.write(f"[{str(datetime.now())[11:16]}]: winner added to leaderboard as {user_name}\n")

    def save_game_vars(self, player_hp, score):
        self.cursor.execute("""
                                    INSERT INTO GameVars
                                    VALUES (?,?,?)
                                    """, (1, "player_hp", player_hp))
        self.cursor.execute("""
                                        INSERT INTO GameVars
                                        VALUES (?,?,?)
                                        """, (1, "score", score))
        self.connection.commit()

    def save_game_sprites(self, sprite_inf):
        self.cursor.execute("""
                                INSERT INTO ObjectProp
                                VALUES (?,?,?,?,?,?,?)
                                """, sprite_inf)
        self.connection.commit()

    def clear_db(self):
        self.cursor.execute("""DELETE FROM SavesData WHERE Save_Id = 1""")
        self.cursor.execute("""DELETE FROM GameVars WHERE Save_ID = 1""")
        self.cursor.execute("""DELETE FROM ObjectProp WHERE Save_ID = 1""")
        self.cursor.execute("""
                    INSERT INTO SavesData
                    VALUES (?,?,?)
                    """, (1, str(datetime.now())[11:16], "quick save"))
        self.connection.commit()

    def load_game(self):
        global player_hp
        global diamonds_left
        data = self.cursor.execute("""
            SELECT ObjectType, ObjectX, ObjectY, ObjectDirX, ObjectDirY, ObjectState
            FROM ObjectProp
            WHERE Save_Id = 1
            """).fetchall()

        for sprite in all_sprites:
            sprite.kill()

        px = 0
        py = 0
        stun = 0
        diamonds_left = 0
        for information in data:
            if information[0] == "Empty":
                Empty('empty', information[1] / 50, information[2] / 50)
            elif information[0] == "Wall":
                Wall('wall', information[1] / 50, information[2] / 50)
            elif information[0] == "Player":
                px, py, stun = information[1], information[2], information[5]
                if stun > FPS * 2:
                    stun = FPS * 2
            elif information[0] == "Diamond":
                Diamond(information[1] / 50, information[2] / 50)
                diamonds_left += 1
            elif information[0] == "GreenSnake":
                GreenSnake(information[1] / 50, information[2] / 50,
                           information[3], information[4], information[5])
        data = self.cursor.execute("""
                SELECT VarName, VarVal
                FROM GameVars
                WHERE Save_Id = 1
                """).fetchall()
        for information in data:
            if information[0] == "player_hp":
                player_hp = information[1]
            if information[0] == "score":
                score = information[1]
        log_file.write(f"[{str(datetime.now())[11:16]}]: game loaded from save file\n")
        return Camera(), Player(px, py, stun), PlayerHP(), score