# mindzie_process_data

**Author:** Soren Frederickson  
**LinkedIn:** https://www.linkedin.com/in/sorenfrederiksen/  
**License:** MIT License - Free for any use

**Feel free to contact me if you have any ideas for other projects I should tackle or data I should generate. I'm happy to talk to anybody about process mining!**

## Overview

This repository contains process mining data and projects available for download and free use under the MIT license. All projects are designed for research, education, and practical implementation of process mining techniques.

## Featured Project: Emergency Department Process Flow Monitor

### 🏥 Hospital Emergency Department Real-Time Monitoring

Our first dataset demonstrates **continuous case flow monitoring** using hospital emergency department data from Alderaan General Hospital. This project showcases how to implement real-time process flow monitoring using process mining techniques.

#### Key Features

- **Real-time Process Monitoring**: Live tracking of patient flow through emergency department stages
- **Command Centre Setup**: Physical dashboard configuration for operational control
- **Historical Analysis**: Traditional process mining for bottleneck identification and optimization
- **Synthetic Data**: Realistic hospital emergency department data for research and education

#### What's Included

- **Complete Mindzie Studio Project** (`Emergency Department/mindzie_studio/Alderaan Hospital.mpz`)
- **Data Generation Scripts** for both historical and real-time datasets
- **Process Stage Definitions** with waiting time thresholds
- **Command Centre Configurations** for operational monitoring
- **Documentation** and process specifications

#### Process Stages Monitored

The system tracks patients through 16 key activities including:
- Patient registration and triage
- Bed assignment and nurse assessment
- Doctor examination and diagnostic testing
- Treatment administration and specialist consultation
- Discharge, admission, or transfer decisions

#### Real-Time Monitoring Capabilities

- **Waiting Time Alerts**: Medium and high threshold monitoring for each stage
- **Current State Tracking**: Live view of all patients currently in the system
- **Operational Dashboards**: Multiple stakeholder views for different roles
- **Performance Metrics**: Duration analysis and bottleneck identification

#### Data Structure

Each event log contains:
- **CaseId**: Unique patient visit identifier
- **ActivityName**: Process step completed
- **ActivityTime**: Timestamp of activity completion
- **PatientID**: Unique patient identifier
- **Additional Attributes**: Age, triage level, vital signs, arrival mode, etc.

#### Quick Start

1. Download the Mindzie Studio project file
2. Upload to your Mindzie Studio environment
3. Explore the real-time monitoring dashboards
4. Generate additional data using the provided Python scripts

## Repository Structure

```
mindzie_process_data/
├── Emergency Department/          # Featured hospital monitoring project
│   ├── mindzie_studio/           # Complete Mindzie Studio project
│   ├── src/                      # Data generation and upload scripts
│   ├── docs/                     # Process specifications and documentation
│   └── Output/                   # Generated datasets (CSV/JSON)
├── [Future Projects]             # Additional process mining datasets
└── LICENSE                       # MIT License
```

## Getting Started

### Prerequisites

- Mindzie Desktop or Mindzie Enterprise access
- Python 3.7+ (for data generation scripts)
- Basic understanding of process mining concepts

### Installation

1. Clone this repository
2. Navigate to the Emergency Department project
3. Follow the project-specific README for detailed setup instructions

## Use Cases

- **Process Mining Research**: Academic and industry research
- **Education**: Learning process mining concepts and techniques
- **Proof of Concept**: Demonstrating real-time monitoring capabilities
- **Training**: Hands-on experience with process mining tools
- **Custom Development**: Building upon the provided data structures

## Contributing

This repository is open for contributions under the MIT license. Feel free to:
- Use the data for any purpose
- Modify and extend the projects
- Share improvements and additional datasets
- Provide feedback and suggestions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Author:** Soren Frederickson  
**LinkedIn:** [LinkedIn Contact - To be added]

---

*This repository provides real-world process mining datasets and projects for the community. All data is synthetic and designed for educational and research purposes.*