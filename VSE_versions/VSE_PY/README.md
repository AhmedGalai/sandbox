# VSE_PY - Visual Scripting Environment (Python)

Python implementation of the Visual Scripting Environment using DearPyGui.

## Features

- Component-based visual scripting system
- Three component types: Publisher, Subscriber, Processor
- Type-safe pin connections
- Execution engine with topological sorting
- Topic-based publish-subscribe system
- JSON-based project serialization
- Interactive node editor using DearPyGui

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Architecture

- `vse_py/core/`: Core system classes (components, pins, parameters, execution engine)
- `vse_py/components/`: Component implementations (math, logic, etc.)
- `vse_py/registry/`: Component factory and registration system
- `vse_py/serialization/`: Project save/load functionality
- `vse_py/gui/`: DearPyGui-based user interface

## Creating Components

See examples in `vse_py/components/math/` for how to create custom components.

## License

MIT
