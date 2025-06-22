# Chinese Checkers Agent

This repository provides the backend engine for a **Chinese Checkers** game, featuring a minimal terminal-based user interface.

It supports matches between human players and computer-controlled opponents, including both **greedy** and **minimax-based** strategies. The core logic handles:

- Game state management  
- Move validation  
- Turn progression  

This forms a solid foundation for extending the game or integrating with more advanced user interfaces.

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/Selvamathuvappan/ChineseCheckers.git
cd ChineseCheckers
```

### Run the Game
```bash
python3 main.py
```

https://github.com/user-attachments/assets/8e74a629-fd06-47b8-9ed4-7b4fdfad853a


https://github.com/user-attachments/assets/1fe78ccd-429f-4109-ad0e-2b6c12cf12fd


By default, you’ll play against a **minimax-based** player.

⚠️ Note:
For better responsiveness in the terminal, it is recommended to:
* Play with only one color per player, or
* Reduce the minimax search depth
(Higher depth and multiple colors will make the Player much slower.)
