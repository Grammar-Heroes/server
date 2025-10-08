from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.db import Base
 # id int
    # user_id int
    # adventure_id string
    # items_collected string[] = {}
    # cleared_nodes string[] = {}
    # current_adaptive_kc string 
    # add_enemy_level int
    # add_enemy_writing_level int
    # add_enemy_defense_level int
    # level int
    # add_writing_level int
    # add_defense_level int
    # current_floor int

    # A) On Starting New Adventure:
    # 1. Login
    # 2. [Loading Screen] Frontend will request for existing Adventure Records (db LoadAdventure())
    # 2. In [Title Screen], press [Play Game]
    # 3. press [Start New Adventure, button that only shows up if record does NOT exist]
    # 4. [Loading Screen] Frontend generates Adventure ID
    # 5. [Loading Screen] Frontend sends to Database
    # 6. [Loading Screen] Database adds new record (db NewAdventure(adventure_id from Frontend))
    # 7. Player enters a stage
    # 8. Player clears the stage
    # 9. [Loading Screen] Frontend adds to its properties (items_collected, cleared_nodes, add_enemy_level, etc.) according to Player choices
    # 10. [Loading Screen] Database updates record (db UpdateAdventure())
    
    # B) On Log-Out or Login with Current Adventure:
    # 1. Log-out
    # 2. Login
    # 3. [Loading Screen] Frontend will request for existing Adventure Records
    # 3. In [Title Screen], press [Play Game]
    # 4. press [Continue Ongoing Adventure, button that only shows up if record exists]
    # 5. [Loading Screen] Database sends record info based on the user id, which stores the Adventure ID, Items Collected, etc... (db LoadAdventure())
    # 6. [Loading Screen] Frontend grabs record info (adventure_id, items_collected, etc.)

    # C) When Getting Adaptive Node
    # 1. After clearing a stage, and the player is about to enter an Adaptive stage, the following occurs:
    # 2. [Loading Screen] Frontend requests the worst KC from backend, stores it as current_adaptive_kc
    # 3. [Loading Screen] Database updates record (db UpdateAdventure())
    # 4. [Loading Screen] Frontend generates the next Adaptive Node according to the worst KC
    
    # D) Functions needed to be defined (that i can think of lol)
    # db NewAdventure() using user ID, if no ongoing adventure, create a new adventure record
    # db UpdateAdventure() using user ID, updates the record with the data from Frontend
    # db LoadAdventure() using user ID, grabs the record and sends to Frontend
    # db ClearRecords() using user ID, clears the record upon Adventure Completion
    # db UpdateAdventureResult() using user ID, stores the relevant information forever in a new model

    # notes: 
    # 1. Loading Screen after Login will always run LoadAdventure()
    # 2. Loading Screen after clearing a stage will always run UpdateAdventure()
    # 3. Loading Screen after pressing Start New Adventure when adventure does not exist will run NewAdventure()
    # 4. Loading Screen after defeating the very final stage will run ClearRecords() and UpdateAdventureResult()

    # Inventory / Progress models won't be necessary, since stored na lahat sa adventure model


    # cleared_nodes = { "node0", "node1a", "node2b", "node3a" }
    # Fae Flower 
    # items_collected = { "fae_flower" }
    # Dragon Skull, Dragon Tooth, The Aegis 
    # items_collected = { "fae_flower", "dragon_skull", "dragon_tooth" }

class Adventure(Base):
    __tablename__ = "adventure"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    adventure_id = Column(String, nullable=False, unique=True) #seed
    items_collected = Column(ARRAY(String), default=list)
    cleared_nodes = Column(ARRAY(String), default=list)
    current_adaptive_kc = Column(String)

    # Stats/Levels
    enemy_level = Column(Integer, default=1)
    enemy_writing_level = Column(Integer, default=1)
    enemy_defense_level = Column(Integer, default=1)
    player_level = Column(Integer, default=1)
    writing_level = Column(Integer, default=1)
    defense_level = Column(Integer, default=1)
    current_floor = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

   