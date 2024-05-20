import openai
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db import connection
import time

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

class ChatbotAPIView(APIView):
    def post(self, request, *args, **kwargs):
        question = request.data.get('question', '')

        if not question:
            return JsonResponse({'error': 'Question not provided'}, status=400)

        # Fetch database schema
        schema = self.get_database_schema()
        examples = self.get_example_data()

        # Retry logic for handling rate limits
        retries = 3
        backoff_factor = 2
        for i in range(retries):
            try:
                # Prepare messages for the model
                messages = [
                    {"role": "system", "content": f"You are an SQL assistant. Given the following database schema and example records, translate the natural language question into an SQL query:\n\n{schema}\n\nExample records:\n\n{examples}\n\n"},
                    {"role": "user", "content": question}
                ]

                # Call ChatCompletion model
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                )


                # Extract SQL query from the response
                sql_query = response.choices[0].message.content.strip('```sql').strip('```').strip()

                # Execute the SQL query
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description]
                    result = cursor.fetchall()

                # Format the result as a list of dictionaries
                formatted_result = [dict(zip(columns, row)) for row in result]

                return JsonResponse({'sql_query': sql_query, 'result': formatted_result})

            except openai.error.RateLimitError:
                if i < retries - 1:
                    time.sleep(backoff_factor ** i)  # Exponential backoff
                else:
                    return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
            except openai.error.InvalidRequestError as e:
                return JsonResponse({'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e), 'result': []}, status=500)




    def get_database_schema(self):
        # Pobranie schematu bazy danych
        schema = """
        Oto zaktualizowana wersja skryptu SQL bez dodatkowych pól `ENGINE`, `DEFAULT CHARACTER SET` i `COLLATE`:

```sql
CREATE TABLE IF NOT EXISTS `perro_scout`.`leagues` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `perro_scout`.`clubs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `league_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `league_id` (`league_id` ASC) VISIBLE,
  CONSTRAINT `clubs_ibfk_1`
    FOREIGN KEY (`league_id`)
    REFERENCES `perro_scout`.`leagues` (`id`)
);

CREATE TABLE IF NOT EXISTS `perro_scout`.`players` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `position` VARCHAR(255) NULL DEFAULT NULL,
  `nationality` VARCHAR(255) NULL DEFAULT NULL,
  `born` INT NULL DEFAULT NULL,
  `club_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `club_id` (`club_id` ASC) VISIBLE,
  CONSTRAINT `players_ibfk_1`
    FOREIGN KEY (`club_id`)
    REFERENCES `perro_scout`.`clubs` (`id`)
);

CREATE TABLE IF NOT EXISTS `perro_scout`.`seasons` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `season` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `perro_scout`.`advanced_goalkeeper` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Goals_GA` INT NULL DEFAULT NULL,
  `Goals_PKA` INT NULL DEFAULT NULL,
  `Goals_FK` INT NULL DEFAULT NULL,
  `Goals_CK` INT NULL DEFAULT NULL,
  `Goals_OG` INT NULL DEFAULT NULL,
  `Expected_PSxG` FLOAT NULL DEFAULT NULL,
  `Expected_PSxG_SoT` FLOAT NULL DEFAULT NULL,
  `Expected_PSxG_Plus_Minus` FLOAT NULL DEFAULT NULL,
  `Expected_Per_90` FLOAT NULL DEFAULT NULL,
  `Launched_Cmp` INT NULL DEFAULT NULL,
  `Launched_Att` INT NULL DEFAULT NULL,
  `Launched_Cmp_Percent` FLOAT NULL DEFAULT NULL,
  `Passes_Att_GK` INT NULL DEFAULT NULL,
  `Passes_Thr` INT NULL DEFAULT NULL,
  `Passes_Launch_Percent` FLOAT NULL DEFAULT NULL,
  `Passes_AvgLen` FLOAT NULL DEFAULT NULL,
  `Goal_Kicks_Att` INT NULL DEFAULT NULL,
  `Goal_Kicks_Launch_Percent` FLOAT NULL DEFAULT NULL,
  `Goal_Kicks_AvgLen` FLOAT NULL DEFAULT NULL,
  `Crosses_Opp` INT NULL DEFAULT NULL,
  `Crosses_Stp` INT NULL DEFAULT NULL,
  `Crosses_Stp_Percent` FLOAT NULL DEFAULT NULL,
  `Sweeper_OPA` INT NULL DEFAULT NULL,
  `Sweeper_OPA_Per_90` FLOAT NULL DEFAULT NULL,
  `Sweeper_AvgDist` FLOAT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `advanced_goalkeeper_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `advanced_goalkeeper_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`goalkeeper`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`goalkeeper` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `MP` INT NULL DEFAULT NULL,
  `Starts` INT NULL DEFAULT NULL,
  `Min` INT NULL DEFAULT NULL,
  `Num_90s` FLOAT NULL DEFAULT NULL,
  `GA` INT NULL DEFAULT NULL,
  `GA90` FLOAT NULL DEFAULT NULL,
  `SoTA` INT NULL DEFAULT NULL,
  `Saves` INT NULL DEFAULT NULL,
  `Save_Percent` FLOAT NULL DEFAULT NULL,
  `W` INT NULL DEFAULT NULL,
  `D` INT NULL DEFAULT NULL,
  `L` INT NULL DEFAULT NULL,
  `CS` INT NULL DEFAULT NULL,
  `CS_Percent` FLOAT NULL DEFAULT NULL,
  `PKatt` INT NULL DEFAULT NULL,
  `PKA` INT NULL DEFAULT NULL,
  `PKsv` INT NULL DEFAULT NULL,
  `PKm` INT NULL DEFAULT NULL,
  `PK_Save_Percent` FLOAT NULL DEFAULT NULL,
  `Matches` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `goalkeeper_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `goalkeeper_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`miscellaneous`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`miscellaneous` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Num_90s` FLOAT NULL DEFAULT NULL,
  `Performance_CrdY` INT NULL DEFAULT NULL,
  `Performance_CrdR` INT NULL DEFAULT NULL,
  `Performance_2CrdY` INT NULL DEFAULT NULL,
  `Performance_Fls` INT NULL DEFAULT NULL,
  `Performance_Fld` INT NULL DEFAULT NULL,
  `Performance_Off` INT NULL DEFAULT NULL,
  `Performance_Crs` INT NULL DEFAULT NULL,
  `Performance_Int` INT NULL DEFAULT NULL,
  `Performance_TklW` INT NULL DEFAULT NULL,
  `Performance_PKwon` INT NULL DEFAULT NULL,
  `Performance_PKcon` INT NULL DEFAULT NULL,
  `Performance_OG` INT NULL DEFAULT NULL,
  `Performance_Recov` INT NULL DEFAULT NULL,
  `Aerial_Duels_Won` INT NULL DEFAULT NULL,
  `Aerial_Duels_Lost` INT NULL DEFAULT NULL,
  `Aerial_Duels_Won_Percent` FLOAT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `miscellaneous_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `miscellaneous_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_club_seasons`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_club_seasons` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `club_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `club_id` (`club_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_club_seasons_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_club_seasons_ibfk_2`
    FOREIGN KEY (`club_id`)
    REFERENCES `perro_scout`.`clubs` (`id`),
  CONSTRAINT `player_club_seasons_ibfk_3`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_defensive_action`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_defensive_action` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Tackles_Tkl` INT NULL DEFAULT NULL,
  `Tackles_TklW` INT NULL DEFAULT NULL,
  `Tackles_Def_3rd` INT NULL DEFAULT NULL,
  `Tackles_Mid_3rd` INT NULL DEFAULT NULL,
  `Tackles_Att_3rd` INT NULL DEFAULT NULL,
  `Challenges_Tkl` INT NULL DEFAULT NULL,
  `Challenges_Att` INT NULL DEFAULT NULL,
  `Challenges_Tkl_Percent` FLOAT NULL DEFAULT NULL,
  `Challenges_Lost` INT NULL DEFAULT NULL,
  `Blocks_Blocks` INT NULL DEFAULT NULL,
  `Blocks_Sh` INT NULL DEFAULT NULL,
  `Blocks_Pass` INT NULL DEFAULT NULL,
  `Int` INT NULL DEFAULT NULL,
  `Tkl_Int` INT NULL DEFAULT NULL,
  `Clr` INT NULL DEFAULT NULL,
  `Err` INT NULL DEFAULT

 NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_defensive_action_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_defensive_action_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_goal_and_shot_creation`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_goal_and_shot_creation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `SCA_SCA` INT NULL DEFAULT NULL,
  `SCA_SCA90` FLOAT NULL DEFAULT NULL,
  `SCA_Types_PassLive` INT NULL DEFAULT NULL,
  `SCA_Types_PassDead` INT NULL DEFAULT NULL,
  `SCA_Types_TO` INT NULL DEFAULT NULL,
  `SCA_Types_Sh` INT NULL DEFAULT NULL,
  `SCA_Types_Fld` INT NULL DEFAULT NULL,
  `SCA_Types_Def` INT NULL DEFAULT NULL,
  `GCA_GCA` INT NULL DEFAULT NULL,
  `GCA_GCA90` FLOAT NULL DEFAULT NULL,
  `GCA_Types_PassLive` INT NULL DEFAULT NULL,
  `GCA_Types_PassDead` INT NULL DEFAULT NULL,
  `GCA_Types_TO` INT NULL DEFAULT NULL,
  `GCA_Types_Sh` INT NULL DEFAULT NULL,
  `GCA_Types_Fld` INT NULL DEFAULT NULL,
  `GCA_Types_Def` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_goal_and_shot_creation_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_goal_and_shot_creation_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_passing`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_passing` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NOT NULL,
  `season_id` INT NOT NULL,
  `Total_Cmp` INT NULL DEFAULT NULL,
  `Total_Att` INT NULL DEFAULT NULL,
  `Total_Cmp_Percent` FLOAT NULL DEFAULT NULL,
  `Total_TotDist` FLOAT NULL DEFAULT NULL,
  `Total_PrgDist` FLOAT NULL DEFAULT NULL,
  `Short_Cmp` INT NULL DEFAULT NULL,
  `Short_Att` INT NULL DEFAULT NULL,
  `Short_Cmp_Percent` FLOAT NULL DEFAULT NULL,
  `Medium_Cmp` INT NULL DEFAULT NULL,
  `Medium_Att` INT NULL DEFAULT NULL,
  `Medium_Cmp_Percent` FLOAT NULL DEFAULT NULL,
  `Long_Cmp` INT NULL DEFAULT NULL,
  `Long_Att` INT NULL DEFAULT NULL,
  `Long_Cmp_Percent` FLOAT NULL DEFAULT NULL,
  `Ast` INT NULL DEFAULT NULL,
  `xAG` FLOAT NULL DEFAULT NULL,
  `Expected_xA` FLOAT NULL DEFAULT NULL,
  `Expected_A_xAG` FLOAT NULL DEFAULT NULL,
  `KP` INT NULL DEFAULT NULL,
  `One_Third` INT NULL DEFAULT NULL,
  `PPA` INT NULL DEFAULT NULL,
  `CrsPA` INT NULL DEFAULT NULL,
  `PrgP` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_passing_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_passing_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_playing_time`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_playing_time` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Playing_Time_MP` INT NULL DEFAULT NULL,
  `Playing_Time_Min` INT NULL DEFAULT NULL,
  `Playing_Time_Mn_MP` FLOAT NULL DEFAULT NULL,
  `Playing_Time_Min_Percent` FLOAT NULL DEFAULT NULL,
  `Num_90s` FLOAT NULL DEFAULT NULL,
  `Starts_Starts` INT NULL DEFAULT NULL,
  `Starts_Mn_Start` FLOAT NULL DEFAULT NULL,
  `Starts_Compl` INT NULL DEFAULT NULL,
  `Subs_Subs` INT NULL DEFAULT NULL,
  `Subs_Mn_Sub` FLOAT NULL DEFAULT NULL,
  `Subs_unSub` INT NULL DEFAULT NULL,
  `Team_Success_PPM` FLOAT NULL DEFAULT NULL,
  `Team_Success_onG` INT NULL DEFAULT NULL,
  `Team_Success_onGA` INT NULL DEFAULT NULL,
  `Team_Success_Plus_Minus` INT NULL DEFAULT NULL,
  `Team_Success_Plus_Minus_90` FLOAT NULL DEFAULT NULL,
  `Team_Success_On_Off` FLOAT NULL DEFAULT NULL,
  `Team_Success_onxG` FLOAT NULL DEFAULT NULL,
  `Team_Success_onxGA` FLOAT NULL DEFAULT NULL,
  `Team_Success_xG_Plus_Minus` FLOAT NULL DEFAULT NULL,
  `Team_Success_xG_Plus_Minus_90` FLOAT NULL DEFAULT NULL,
  `Team_Success_xG_On_Off` FLOAT NULL DEFAULT NULL,
  `Matches` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_playing_time_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_playing_time_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_possession`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_possession` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Touches` INT NULL DEFAULT NULL,
  `Touches_Def_Pen` INT NULL DEFAULT NULL,
  `Touches_Def_3rd` INT NULL DEFAULT NULL,
  `Touches_Mid_3rd` INT NULL DEFAULT NULL,
  `Touches_Att_3rd` INT NULL DEFAULT NULL,
  `Touches_Att_Pen` INT NULL DEFAULT NULL,
  `Touches_Live` INT NULL DEFAULT NULL,
  `Take_Ons_Att` INT NULL DEFAULT NULL,
  `Take_Ons_Succ` INT NULL DEFAULT NULL,
  `Take_Ons_Succ_Percent` FLOAT NULL DEFAULT NULL,
  `Take_Ons_Tkld` INT NULL DEFAULT NULL,
  `Take_Ons_Tkld_Percent` FLOAT NULL DEFAULT NULL,
  `Carries` INT NULL DEFAULT NULL,
  `Carries_TotDist` INT NULL DEFAULT NULL,
  `Carries_PrgDist` INT NULL DEFAULT NULL,
  `Carries_PrgC` INT NULL DEFAULT NULL,
  `Carries_1_3` INT NULL DEFAULT NULL,
  `Carries_CPA` INT NULL DEFAULT NULL,
  `Carries_Mis` INT NULL DEFAULT NULL,
  `Carries_Dis` INT NULL DEFAULT NULL,
  `Receiving_Rec` INT NULL DEFAULT NULL,
  `Receiving_PrgR` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_possession_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_possession_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`player_shooting`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`player_shooting` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `Gls` INT NULL DEFAULT NULL,
  `Sh` INT NULL DEFAULT NULL,
  `SoT` INT NULL DEFAULT NULL,
  `Sot_pr` FLOAT NULL DEFAULT NULL,
  `Sh_90` FLOAT NULL DEFAULT NULL,
  `SoT_90` FLOAT NULL DEFAULT NULL,
  `G_Sh` FLOAT NULL DEFAULT NULL,
  `G_SoT` FLOAT NULL DEFAULT NULL,
  `Dist` FLOAT NULL DEFAULT NULL,
  `FK` INT NULL DEFAULT NULL,
  `PK` INT NULL DEFAULT NULL,
  `PKatt` INT NULL DEFAULT NULL,
  `xG` FLOAT NULL DEFAULT NULL,
  `npxG`

 FLOAT NULL DEFAULT NULL,
  `npxG_Sh` FLOAT NULL DEFAULT NULL,
  `G_xG` FLOAT NULL DEFAULT NULL,
  `np_G_xG` FLOAT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `player_shooting_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `player_shooting_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`ratings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`ratings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `season_id` INT NULL DEFAULT NULL,
  `rating` FLOAT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  INDEX `season_id` (`season_id` ASC) VISIBLE,
  CONSTRAINT `ratings_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`),
  CONSTRAINT `ratings_ibfk_2`
    FOREIGN KEY (`season_id`)
    REFERENCES `perro_scout`.`seasons` (`id`)
);

-- -----------------------------------------------------
-- Table `perro_scout`.`values`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `perro_scout`.`values` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL DEFAULT NULL,
  `value` FLOAT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `player_id` (`player_id` ASC) VISIBLE,
  CONSTRAINT `values_ibfk_1`
    FOREIGN KEY (`player_id`)
    REFERENCES `perro_scout`.`players` (`id`)
);
```

Teraz wszystkie tabele nie mają pól `ENGINE`, `DEFAULT CHARACTER SET` oraz `COLLATE`.
        """
        return schema

    def get_example_data(self):
        # Pobranie przykładowych danych z bazy danych
        examples = ""
        with connection.cursor() as cursor:
            # Przykładowe dane z tabeli players
            cursor.execute("SELECT * FROM players LIMIT 5")
            players = cursor.fetchall()
            examples += "Players: " + str(players) + "\n"

            # Przykładowe dane z tabeli clubs
            cursor.execute("SELECT * FROM clubs LIMIT 5")
            clubs = cursor.fetchall()
            examples += "Clubs: " + str(clubs) + "\n"

            # Przykładowe dane z tabeli leagues
            cursor.execute("SELECT * FROM leagues LIMIT 5")
            leagues = cursor.fetchall()
            examples += "Leagues: " + str(leagues) + "\n"

        return examples
