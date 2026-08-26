# IROS 2026 로봇 Reasoning 논문 전체 목록 및 연구 동향 분석

## 1. 분석 개요

IROS 2026의 전체 프로그램 1,933편에서 `reasoni`를 검색해 나온 64편을 정리하고, 이들이 다루는 reasoning의 종류와 연구 흐름을 분석하였다.

이 목록을 해석할 때는 검색 방식의 한계를 먼저 고려해야 한다. 검색 결과 64편이 모두 제목에 `reasoning`을 포함하는 것은 아니다. 일부는 `Representing 3D Space for Robot Reasoning`, `Learned Reasoning and Dynamics Models in Robotics`처럼 세션명에 검색어가 포함되어 같은 세션의 논문들이 함께 검색된 경우다.

따라서 본 문서에서는 다음 두 유형을 구분한다.

- **직접:** 논문 제목에 `reason` 또는 `reasoning`이 직접 포함된 논문
- **문맥:** 제목에는 포함되지 않지만 reasoning 관련 세션에 배치되어 검색된 논문

설명은 제공된 IROS 2026 프로그램의 제목·세션·저자 키워드에 근거한 보수적 해석이다. 초록과 본문을 확인한 개별 논문 리뷰와는 구분해야 한다.

## 2. 핵심 결론

IROS 2026의 로봇 reasoning은 단순히 “LLM이 생각을 언어로 출력하게 하는 것”에서 벗어나 다음 방향으로 발전하고 있다.

1. Reasoning을 **PDDL, 코드, scene graph, 기하 제약, temporal logic과 같은 실행 가능한 중간표현**으로 변환한다.
2. 언어와 행동을 한 번에 생성하기보다 **reasoning과 action을 분리하거나 교차·병렬화**한다.
3. 모든 시점에 깊은 reasoning을 수행하지 않고 **불확실하거나 실패 가능성이 클 때만 선택적으로 호출**한다.
4. 작업 성공뿐 아니라 **실패 탐지, 복구, 자기검증, 경험 활용, 실시간성**을 reasoning 시스템의 일부로 본다.
5. 공간 reasoning에서는 모델 크기보다 **persistent representation과 memory**가 핵심 기반으로 부상한다.

## 3. 검색 결과의 규모

| 구분 | 논문 수 | 전체 1,933편 대비 |
|---|---:|---:|
| 제목에 `reason`이 직접 포함 | 35편 | 1.81% |
| 세션명 때문에 함께 검색 | 29편 | 1.50% |
| 전체 검색 결과 | 64편 | 3.31% |

35편은 제목에 기반한 lexical lower bound다. 반대로 `PIP-LLM`, `RoboPilot`, `AtomTree`처럼 제목에 reasoning이라는 단어가 없어도 실질적으로 reasoning을 다루는 논문이 있다. 따라서 64편 전체를 reasoning 및 reasoning-adjacent 연구군으로 보는 것이 적절하다.

## 4. 기능적 분류

| 연구 분야 | 전체 | 직접 | 문맥 |
|---|---:|---:|---:|
| 장기 계획·형식 추론·에이전트 구조 | 15 | 6 | 9 |
| VLA·조작·접촉 reasoning | 10 | 10 | 0 |
| 공간·3D·내비게이션 reasoning | 16 | 9 | 7 |
| 다중 로봇·시간·동역학 | 7 | 1 | 6 |
| 자율주행 behavior reasoning | 9 | 2 | 7 |
| 도메인 특화·안전·진단 | 7 | 7 | 0 |
| **합계** | **64** | **35** | **29** |

특히 VLA·조작 그룹의 10편이 모두 제목에서 reasoning을 직접 표방한다. Reasoning이 단순한 포괄적 표현을 넘어 VLA architecture의 핵심 경쟁축이 되었음을 보여준다.

# 5. 전체 64편 목록과 분류

## 5.1 장기 계획·형식 추론·에이전트 구조: 15편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #3440 | **AERMANI-VLM: Structured Prompting and Reasoning for Aerial Manipulation with Vision Language Models** | 구조화된 prompting과 reasoning으로 aerial manipulation의 작업 이해와 행동 생성을 연결한다. |
| 직접 | #3990 | **VL-Nav: A Neuro-Symbolic Approach for Reasoning-Based Vision-Language Navigation** | VLM의 의미 이해와 symbolic reasoning을 결합한 neuro-symbolic VLN이다. IROS Best Paper Award on Cognitive Robotics 후보이기도 하다. |
| 문맥 | #484 | **RoboPilot: Generalizable Dynamic Robotic Manipulation with Dual-Thinking Modes** | 동적 조작에서 서로 다른 두 thinking mode를 사용하는 구조다. 빠른 반응과 숙고형 계획의 분리 가능성을 보여준다. |
| 직접 | #2620 | **REFLEX: Metacognitive Reasoning for Reflective Zero-Shot Robotic Planning with Large Language Models** | LLM이 자신의 계획을 검토하고 수정하는 metacognitive zero-shot planning이다. |
| 문맥 | #2298 | **Constrained Neuro-Symbolic Framework for Knowledge-Driven Task and Motion Planning** | 지식 기반 symbolic planning에 제약 조건과 motion planning을 결합한다. |
| 문맥 | #1480 | **Demonstration-Free Robotic Control Via LLM Agents** | 시연 데이터 없이 LLM agent가 작업을 해석하고 제어 절차를 생성한다. |
| 직접 | #837 | **LOGICWorld: Automated Deep Logic Generation for Interactive Reasoning in Embodied Agents** | Embodied agent의 논리 추론을 평가하기 위한 복잡한 논리 문제를 자동 생성한다. |
| 문맥 | #132 | **Robotic Long-Horizon Manipulation with Progressive In-Context Code Generation and Episodic Feedback** | 장기 조작을 코드로 점진적으로 생성하고 이전 실행의 episodic feedback을 이용해 수정한다. |
| 문맥 | #326 | **Grounded Vision-Language Interpreter for Long-Horizon Bimanual Task and Motion Planning** | 언어 명령을 grounded representation으로 변환해 장기 양손 TAMP에 연결한다. |
| 문맥 | #2469 | **Geometric Constraints As General Interfaces for Robot Manipulation** | 언어 및 task specification과 저수준 조작 사이의 인터페이스로 기하 제약을 사용한다. |
| 문맥 | #1067 | **PhaseBot: A Phase-Gated Understanding-Generation-Action Model for Long-Horizon Contact Manipulation** | 접촉 조작을 phase 단위로 나누고 understanding–generation–action을 단계적으로 작동시킨다. |
| 직접 | #4594 | **Differentiable SpaTiaL: Symbolic Learning and Reasoning with Geometric Temporal Logic for Manipulation Tasks** | Geometric temporal logic을 differentiable하게 만들어 symbolic reasoning과 학습을 연결한다. |
| 문맥 | #1137 | **AtomTree: A Hierarchical Framework for State-Aware Embodied Instruction Following with LLMs** | 지시를 계층적으로 분해하고 현재 상태를 반영해 실행하는 LLM instruction-following 구조다. |
| 문맥 | #2690 | **EmboAlign: Aligning Video Generation with Compositional Constraints for Zero-Shot Manipulation** | 생성 비디오가 조작 작업의 compositional constraint를 만족하도록 정렬한다. Video world model을 계획에 활용하는 흐름이다. |
| 직접 | #1724 | **Embodied Chain-Of-Thought Model Via Interleaved Reasoning** | Reasoning과 embodied prediction 또는 action을 분리된 단계가 아니라 교차 형태로 수행한다. |

이 그룹의 핵심 변화는 free-form Chain-of-Thought에서 typed intermediate representation으로의 이동이다. 코드, PDDL, temporal logic, geometric constraint, task tree가 언어와 제어 사이의 실행 가능성 및 안전성 검증 장치로 사용된다.

## 5.2 VLA·조작·접촉 reasoning: 10편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #268 | **ICLR: In-Context Imitation Learning with Visual Reasoning** | 새로운 시연을 parameter update 없이 문맥에서 해석하고 visual reasoning을 통해 모방한다. |
| 직접 | #2619 | **A Robust Placeability Metric for Model-Free Unified Pick-And-Place Reasoning** | 물체를 어디에 안정적으로 놓을 수 있는지를 model-free metric으로 판단해 pick-and-place를 통합한다. |
| 직접 | #1208 | **Incentivizing Multimodal Reasoning in Large Models for Direct Robot Manipulation** | Direct action prediction 과정에서 실제 multimodal reasoning을 수행하도록 학습 목표를 설계한다. |
| 직접 | #3240 | **Test-Time Spatial Reasoning for Robot Manipulation Using Generative Real-to-Sim** | 실제 관측을 test time에 시뮬레이션 가능한 장면으로 변환해 공간관계와 조작 결과를 추론한다. |
| 직접 | #1923 | **VCoT-Grasp: Grasp Foundation Models with Visual Chain-Of-Thought Reasoning for Language-Driven Grasp Generation** | Grasp foundation model이 최종 grasp를 바로 출력하지 않고 시각적 중간 reasoning을 생성한다. |
| 직접 | #2265 | **Hybrid Chain-Of-Thought Reasoning for Vision–Language–Action Models** | 서로 다른 형태의 CoT를 결합해 VLA의 계획과 실행을 개선한다. |
| 직접 | #1811 | **DialogVLA: Bridging Reasoning Action in Bimanual Manipulation Via Parallel Mixture-Of-Experts** | Parallel mixture-of-experts를 이용해 reasoning 경로와 action 경로를 연결하는 양손 조작 모델이다. |
| 직접 | #2500 | **DualCoT-VLA: Visual-Linguistic Chain of Thought Via Parallel Reasoning for Vision-Language-Action Models** | Visual CoT와 linguistic CoT를 병렬로 구성해 공간정보와 언어적 추상화를 상호 보완한다. |
| 직접 | #725 | **FailSafe: Reasoning and Recovery from Failures in Vision-Language-Action Models** | VLA가 실패를 인식하고 원인을 추론한 후 recovery action을 생성한다. |
| 직접 | #1122 | **TacReasoner: A Dynamic Tactile-Language Framework for Interactive Reasoning in Real-World Scenarios** | Tactile signal과 언어를 동적으로 결합해 접촉 상태를 해석하고 상호작용 전략을 갱신한다. |

이 그룹에서는 reasoning channel의 설계가 핵심 경쟁축이다.

- Visual CoT
- Linguistic CoT
- Hybrid CoT
- Interleaved reasoning
- Parallel reasoning and action
- Tactile-language reasoning
- Test-time simulation-based reasoning

Robotics의 CoT는 텍스트 문장을 길게 생성하는 방법이 아니라 미래 영상, affordance, 접촉 상태, trajectory, latent feature를 포함하는 multimodal computation graph로 확장되고 있다.

## 5.3 공간·3D·내비게이션 reasoning: 16편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #2564 | **SG-DOR: Learning Scene Graphs with Direction-Conditioned Occlusion Reasoning for Pepper Plants** | 식물의 가려진 구조를 방향 조건과 scene graph를 이용해 추론한다. |
| 직접 | #3321 | **GeoReFormer: Geometry-Aware Refinement for Lane Segment Detection and Topology Reasoning** | Lane segment의 국소 검출과 도로망 topology reasoning을 결합한다. |
| 직접 | #959 | **SoraNav: Adaptive UAV Task-Centric Navigation Via Zero-Shot VLM Reasoning** | Zero-shot VLM reasoning을 이용해 UAV의 task-centric navigation을 적응시킨다. |
| 직접 | #2212 | **RoBoSR: Structured Scene Representations for Embodied Robotic Reasoning** | Embodied reasoning에 적합한 structured scene representation을 구축한다. |
| 직접 | #2691 | **Splatting As Attention: Reasoning in 3D Gaussian Fields for Occupancy Prediction in Autonomous Driving** | 3D Gaussian field에서 attention을 수행해 자율주행 occupancy를 추론한다. |
| 직접 | #1246 | **ViSA-Enhanced Aerial VLN: A Visual-Spatial Reasoning Framework for Aerial Vision-Language Navigation** | Aerial VLN에 명시적인 visual-spatial reasoning 모듈을 추가한다. |
| 문맥 | #3831 | **3D Scene Graph Prediction: Generating Hierarchical Models from Partially Observed Environments** | 부분 관측으로부터 계층적인 3D scene graph를 생성한다. |
| 문맥 | #1324 | **From Pixels to Concepts: Growing Rich 3D Semantic Scene Graph Forests Utilizing Foundation Models** | Foundation model을 이용해 관측이 축적될수록 확장되는 3D semantic scene-graph forest를 구축한다. |
| 문맥 | #1006 | **HyProSG: A Hyperbolic Prototype Network for Hierarchical 3D Scene Graph Generation** | Hyperbolic space의 계층 표현 능력을 이용해 3D scene graph를 생성한다. |
| 문맥 | #2448 | **TerraAlign: Language-Supervised Alignment of Vision and Proprioception for Multi-Grained Terrain Classification** | 언어 supervision으로 vision과 proprioception을 정렬해 여러 수준의 terrain semantics를 학습한다. |
| 문맥 | #4772 | **STaR: Scalable Task-Conditioned Retrieval for Long-Horizon Multimodal Robot Memory** | 장기 작업에 필요한 multimodal memory만 task-conditioned retrieval로 가져온다. |
| 문맥 | #553 | **3D UAV Trajectory Estimation and Classification from Internet Videos Via Language Model** | 인터넷 영상과 language model을 이용해 UAV의 3D trajectory와 행동 유형을 복원한다. |
| 문맥 | #2133 | **DeNoise2Completion: Diffusion-Based Unified Model for Point Cloud Denoising and Completion** | Diffusion으로 point-cloud denoising과 completion을 통합한다. Reasoning보다는 입력 표현 복원에 가깝다. |
| 직접 | #385 | **Scene-Q: Confidence-Aware Coarse-To-Fine Querying of 3D Scenes with Selective VLM Reasoning** | 장면의 불확실도에 따라 coarse-to-fine VLM query를 선택적으로 수행한다. |
| 직접 | #4453 | **Perception-Aware Multimodal Spatial Reasoning from Monocular Images** | Monocular image의 관측 한계를 고려하면서 여러 modality로 공간관계를 추론한다. |
| 직접 | #1835 | **Frontier-as-Token: Structured Spatial Reasoning for Zero-shot Object Navigation** | Exploration frontier를 VLM이 직접 다룰 수 있는 token으로 표현해 zero-shot object navigation을 수행한다. |

이 분야에서는 reasoning보다 representation이 먼저라는 점이 분명하게 나타난다. 모델이 공간을 image token만으로 다루면 metric relation, visibility, topology, persistence를 안정적으로 추론하기 어렵다. 이에 따라 다음 표현들이 reasoning substrate로 등장한다.

- 3D scene graph
- Hierarchical and hyperbolic representation
- 3D Gaussian field
- Frontier token
- Multimodal memory
- Language-aligned terrain representation
- Generative real-to-sim scene

특히 Scene-Q는 모든 장면에 VLM을 무겁게 호출하지 않고 confidence에 따라 reasoning resolution과 비용을 조절한다. 이는 runtime reasoning budget 연구와 직접 연결되는 흐름이다.

## 5.4 다중 로봇·시간·동역학 reasoning: 7편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #5007 | **WinkTPG: An Execution Framework for Multi-Agent Path Finding Using Temporal Reasoning** | Multi-agent path finding 결과를 temporal reasoning으로 충돌 없이 실행한다. |
| 문맥 | #311 | **IndoorR2X: Indoor Robot-To-Everything Coordination with LLM-Driven Planning** | LLM planning을 이용해 실내 로봇과 주변 장치 및 인프라의 협업을 조정한다. |
| 문맥 | #430 | **Physics-Informed Neural Controlled Differential Equations for Scalable Long Horizon Multi-Agent Motion Forecasting** | 물리 prior와 neural controlled differential equation으로 장기 multi-agent motion을 예측한다. |
| 문맥 | #925 | **PIP-LLM: Integrating PDDL-Integer Programming with LLMs for Coordinating Multi-Robot Teams Using Natural Language** | 자연어는 LLM이 해석하고 PDDL과 integer programming이 다중 로봇 계획의 실행 가능성을 보장한다. |
| 문맥 | #4156 | **ST-GRL: Spatiotemporal Cognitive Graph Reinforcement Learning for Scalable Multi-Robot Collaborative Exploration** | Spatiotemporal cognitive graph와 RL을 결합해 대규모 다중 로봇 탐사를 수행한다. |
| 문맥 | #4450 | **Distilling Collaborative Dynamics into Latent Space for Implicit Coordination in Decentralized Multi-Agent Manipulation** | 협업 동역학을 latent representation으로 증류해 명시적 통신 없이 coordination을 학습한다. |
| 문맥 | #947 | **Articulated-Body Dynamics Network: Dynamics-Grounded Prior for Robot Learning** | Articulated-body dynamics를 학습 모델의 prior로 사용해 물리적으로 타당한 robot learning을 유도한다. |

다중 로봇 reasoning은 자연어 CoT보다 최적화, 그래프, 동역학 모델, 시간 제약의 형태로 구현되는 경우가 많다. PIP-LLM은 이 역할 분담을 잘 보여준다.

```text
Natural language
    → LLM interpretation
    → PDDL task model
    → Integer programming
    → Feasible multi-robot plan
```

LLM은 열린 언어의 의미를 처리하지만 allocation과 feasibility는 고전적 solver가 담당한다. 현재로서는 end-to-end LLM보다 검증 가능성이 높은 구조다.

## 5.5 자율주행 behavior reasoning: 9편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #3793 | **CARLA-GS: Decoupling Representation, Reasoning, and Physics Simulation for Autonomous Driving Corner-Case Synthesis** | Scene representation, semantic reasoning, physics simulation을 분리해 corner-case driving scene을 생성한다. |
| 문맥 | #450 | **Closing the Navigation Compliance Gap in End-To-End Autonomous Driving** | E2E driving 모델이 주어진 route 또는 navigation command를 제대로 따르지 않는 문제를 다룬다. |
| 문맥 | #1420 | **Driver-State-Aware Risk Assessment and Driving Assistance Based on an End-To-End Model** | 운전자 상태를 포함해 위험을 추정하고 driving assistance를 결정한다. |
| 문맥 | #3528 | **HiD2: A Trajectory Generator for High-Density Traffic and Diverse Agent-Interaction Scenarios** | 고밀도 교통과 다양한 agent interaction을 포함하는 trajectory scenario를 생성한다. |
| 문맥 | #650 | **Chat2Scenic: An Iterative RAG-Based Framework for Scenario Generation in Autonomous Driving** | RAG와 반복적 대화를 이용해 자연어 요구사항을 Scenic 기반 driving scenario로 변환한다. |
| 문맥 | #2464 | **Super Agents and Confounders: Influence of Surrounding Agents on Vehicle Trajectory Prediction** | 주변 차량 중 어떤 agent가 ego trajectory prediction에 실제 영향을 주는지 분석한다. |
| 문맥 | #1249 | **Unified Early Traffic Conflict Detection for Autonomous Vehicles Via Future Trajectory Prediction** | 미래 trajectory를 예측해 충돌보다 이른 단계에서 traffic conflict를 탐지한다. |
| 문맥 | #638 | **PEDRA: PErsonalized Driving Representation for Autonomy** | 운전자 또는 사용자별 driving preference를 representation으로 학습한다. |
| 직접 | #317 | **DiffAttn: Diffusion-Based Drivers' Visual Attention Prediction with LLM-Enhanced Semantic Reasoning** | LLM의 semantic reasoning과 diffusion을 결합해 운전자의 시각적 attention을 예측한다. |

이 그룹은 CoT보다 행동 예측, scenario generation, personalization, risk assessment에 가깝다. 자율주행 분야에서는 reasoning을 타 차량과 운전자의 의도 및 미래 행동을 구조적으로 예측하는 넓은 의미로 사용한다.

## 5.6 수술·산업·수중·UAV·안전 reasoning: 7편

| 구분 | 번호 | 논문 | 핵심 내용 |
|---|---:|---|---|
| 직접 | #4429 | **Vision-Language Procedural Reasoning for Context-Aware Reward Modeling of Robotic Endovascular Guidewire Navigation** | 수술 절차의 맥락을 VLM이 해석하고 이를 guidewire navigation용 reward modeling에 사용한다. |
| 직접 | #4989 | **SurgRAW: Multi-Agent Workflow with Chain of Thought Reasoning for Robotic Surgical Video Analysis** | 여러 agent와 CoT를 이용해 수술 영상의 단계, 상태, workflow를 분석한다. |
| 직접 | #1413 | **CognitiveDrone: A VLA Model and Evaluation Benchmark for Real-Time Cognitive Task Solving and Reasoning in UAVs** | UAV의 실시간 cognitive task solving과 reasoning을 평가하는 VLA 모델 및 benchmark다. |
| 직접 | #1383 | **Don't Fool Me Twice: Adapting to Adversity in the Wild with Experience-Driven Reasoning** | 현장 실패 경험을 기억해 이후 유사한 adversity에 적응하는 experience-driven reasoning이다. |
| 직접 | #5060 | **WeldLLM: A Multimodal Framework for Welding Defect Detection and Automated Diagnostic Reasoning** | 용접 결함을 검출하는 데서 끝나지 않고 원인 또는 상태를 자동 진단한다. |
| 직접 | #2143 | **A Collaborative Reasoning Framework for Anomaly Diagnostics in Underwater Robotics** | 여러 모델, agent, 센서 정보를 결합해 수중 로봇 이상 원인을 진단한다. |
| 직접 | #1666 | **CORAL: COntextual Reasoning and Local Planning in A Hierarchical VLM Framework for Underwater Monitoring** | Hierarchical VLM이 환경 맥락을 추론하고 하위 local planner가 수중 monitoring 행동을 수행한다. |

Reasoning이 safety-critical domain으로 들어가면서 복잡한 작업 수행 자체보다 진단 가능성, 절차 준수, 실패 복구가 중요한 연구 목표로 부상하고 있다.

# 6. IROS 2026에서 나타나는 핵심 연구 흐름

## 6.1 Reasoning은 단일 모델이 아니라 시스템 구조다

이 논문들에서 reasoning은 단일 transformer 내부의 추상적 능력으로만 다뤄지지 않는다. 대체로 다음과 같은 폐루프 시스템으로 구성된다.

```text
Multimodal observation
    → Structured representation
    → Reasoning or planning
    → Constraint verification
    → Action execution
    → Feedback and recovery
    → Representation and belief update
```

핵심 경쟁은 foundation model의 크기보다 다음 질문으로 이동하고 있다.

- 어떤 중간표현을 사용할 것인가?
- 언제 reasoning을 수행할 것인가?
- Reasoning 결과를 어떻게 검증할 것인가?
- 실패 이후 belief와 plan을 어떻게 갱신할 것인가?

## 6.2 더 길게 생각하기보다 필요할 때만 생각하기

다음 논문들은 selective reasoning의 초기 형태를 보여준다.

- **RoboPilot:** 복수 thinking mode
- **Scene-Q:** confidence-aware selective querying
- **REFLEX:** 계획에 대한 reflective reasoning
- **FailSafe:** 실패 탐지 이후 reasoning과 recovery
- **DialogVLA:** reasoning expert와 action expert의 분리
- **Don't Fool Me Twice:** 과거 실패 경험의 재사용

실시간 로봇에서는 긴 CoT를 매 시점 실행할 수 없다. 따라서 reasoning depth는 다음과 같이 상태 의존적으로 결정되어야 한다.

\[
\text{reasoning depth}_t
= f(\text{uncertainty}_t,\,\text{risk}_t,\,\text{novelty}_t,\,\text{time budget}_t).
\]

개별 논문들은 이 요소들의 일부를 다루지만 uncertainty, risk, novelty, latency를 통합해 reasoning budget을 배분하는 일반적 프레임워크는 아직 확립되지 않았다.

## 6.3 Spatial reasoning은 VLM보다 representation과 memory의 문제다

공간 reasoning 분야에서는 scene graph, Gaussian field, frontier token, multimodal memory가 반복적으로 등장한다. 이미지 한 장을 언어로 해석하는 VLM만으로 다음 문제를 안정적으로 처리하기 어렵기 때문이다.

- 부분 관측과 가려짐
- 시점 변화
- metric distance와 방향
- topology와 connectivity
- 장기적인 상태 변화
- 이동 중 누적되는 evidence
- 행동에 따라 달라지는 관측 가능성

따라서 유망한 방향은 단순히 VLM에 3D 질문을 입력하는 것이 아니다. Persistent spatial memory에서 필요한 evidence를 검색하고, belief를 갱신하며, 필요하면 능동적으로 추가 관측을 획득해야 한다.

## 6.4 CoT 자체보다 grounding과 검증이 병목이다

텍스트 rationale이 길다고 실제 reasoning이 좋아졌다고 볼 수는 없다. 강한 embodied reasoning 연구를 위해서는 최소한 다음을 분리해 평가해야 한다.

- Rationale을 바꾸면 행동도 인과적으로 바뀌는가?
- 중간 reasoning이 실제 장면 및 센서 evidence와 일치하는가?
- 불가능한 계획을 스스로 탐지하는가?
- Constraint violation이 감소하는가?
- Unseen composition에서 일반화되는가?
- Reasoning의 추가 비용 대비 성공률 이득이 충분한가?
- 설명은 틀렸지만 행동은 맞는 경우를 어떻게 처리하는가?

앞으로의 핵심은 CoT generation보다 **grounded, causal, executable reasoning**이다.

## 6.5 고전적 robotics가 reasoning의 검증기로 돌아왔다

이번 목록에는 PDDL, integer programming, temporal logic, geometric constraint, physics prior, scene graph가 다수 등장한다. 이는 LLM이 classical planning을 완전히 대체하는 방향보다는 다음과 같은 역할 분담으로의 수렴을 시사한다.

> LLM과 VLM은 열린 언어 및 의미를 처리하고, 고전적 최적화와 기하·물리 모듈은 실행 가능성과 안전성을 보장한다.

# 7. 우선적으로 확인할 논문

## 7.1 Spatial intelligence, VLN, memory, runtime reasoning 관점

1. **VL-Nav** — neuro-symbolic VLN이며 Cognitive Robotics Best Paper 후보
2. **Scene-Q** — confidence-aware selective reasoning과 runtime budget
3. **RoBoSR** — reasoning을 위한 structured scene representation
4. **Frontier-as-Token** — classical exploration primitive와 foundation model token의 결합
5. **REFLEX** — metacognition과 plan revision
6. **FailSafe** — failure reasoning과 recovery
7. **Test-Time Spatial Reasoning via Generative Real-to-Sim** — test-time world construction과 action evaluation
8. **3D Scene Graph Prediction** — partial observation과 hierarchical spatial representation
9. **STaR** — 장기 multimodal memory의 task-conditioned retrieval
10. **ViSA-Enhanced Aerial VLN** — aerial domain의 명시적 spatial reasoning

## 7.2 VLA architecture 관점

다음 여섯 편을 함께 비교하면 2026년 VLA reasoning architecture의 주요 설계 공간을 파악할 수 있다.

- **Hybrid Chain-of-Thought Reasoning for VLA Models**
- **DualCoT-VLA**
- **DialogVLA**
- **Embodied Chain-of-Thought via Interleaved Reasoning**
- **VCoT-Grasp**
- **Incentivizing Multimodal Reasoning for Direct Robot Manipulation**

비교할 핵심 축은 다음과 같다.

| 비교 축 | 주요 질문 |
|---|---|
| Reasoning modality | Text, image, video, tactile, latent 중 무엇을 사용하는가? |
| Temporal organization | 순차적, interleaved, parallel 중 어느 구조인가? |
| Action coupling | Reasoning과 action이 같은 decoder를 사용하는가? |
| Supervision | CoT annotation, reward, imitation, self-generated rationale 중 무엇인가? |
| Verification | 중간 reasoning의 정확성과 실행 가능성을 어떻게 검사하는가? |
| Runtime cost | Reasoning이 latency와 control frequency에 미치는 영향은 무엇인가? |

# 8. 유망한 future-work gap

가장 큰 빈틈은 “어떻게 reasoning할 것인가”보다 **언제, 얼마나, 무엇을 대상으로 reasoning할 것인가**다.

구체적으로 다음 연구 문제가 유망하다.

1. Confidence와 위험도에 따른 adaptive reasoning depth
2. Spatial memory retrieval와 reasoning budget의 공동 최적화
3. Answer, act, ask, observe 사이의 능동적 선택
4. Verbal CoT와 실제 action causality를 분리하는 평가법
5. Reasoning latency와 control deadline의 공동 스케줄링
6. 실패 경험을 장기 memory로 축적하고 재사용하는 방법
7. 여러 agent가 긴 CoT 대신 compressed belief 또는 constraint를 공유하는 방법
8. Scene graph, code, trajectory 중 적절한 중간표현을 선택하는 meta-controller
9. 동일 성공률에서 reasoning token, latency, energy를 최소화하는 학습
10. 모델의 confidence가 아니라 실제 task-level failure probability에 기반한 reasoning trigger

## 8.1 특히 비어 있는 통합 문제

현재 논문들은 confidence-aware query, reflection, recovery, memory retrieval, fast/slow mode를 각각 다룬다. 그러나 이를 하나의 정책으로 통합한 연구는 드물다.

통합 정책은 매 시점 다음 행동 중 하나를 선택할 수 있어야 한다.

\[
a_t^{\mathrm{meta}}
\in
\{\text{act},\,\text{reason},\,\text{retrieve},\,\text{observe},\,\text{ask},\,\text{recover}\}.
\]

이때 목표는 단순 성공률 최대화가 아니라 다음과 같은 비용을 함께 고려하는 것이다.

\[
J
=
\mathbb{E}\left[
R_{\mathrm{task}}
- \lambda_1 C_{\mathrm{latency}}
- \lambda_2 C_{\mathrm{compute}}
- \lambda_3 C_{\mathrm{risk}}
- \lambda_4 C_{\mathrm{interaction}}
\right].
\]

이 문제는 runtime reasoning budget, active perception, interactive clarification, memory retrieval를 하나의 embodied decision problem으로 묶을 수 있다.

# 9. 최종 인사이트

IROS 2026의 가장 큰 메시지는 다음과 같이 요약할 수 있다.

> 로봇 reasoning의 경쟁은 더 이상 “LLM이 계획을 생성할 수 있는가”가 아니다. 이제는 생성된 계획이 공간적으로 grounded되어 있고, 물리적으로 실행 가능하며, 불확실성을 인식하고, 제한된 시간 안에 검증·수정될 수 있는가가 핵심이다.

현재의 연구는 reasoning capability를 추가하는 단계에서 reasoning을 관리하는 단계로 이동하고 있다. 다음 세대의 강한 시스템은 가장 긴 CoT를 생성하는 모델이 아니라, **필요한 순간을 인식하고 적절한 표현과 계산량으로 reasoning한 뒤 그 결과를 행동과 검증으로 닫을 수 있는 모델**일 가능성이 높다.

---

## 부록: 원 검색 순서 기준 64편 인덱스

1. #5007 WinkTPG: An Execution Framework for Multi-Agent Path Finding Using Temporal Reasoning
2. #3440 AERMANI-VLM: Structured Prompting and Reasoning for Aerial Manipulation with Vision Language Models
3. #3990 VL-Nav: A Neuro-Symbolic Approach for Reasoning-Based Vision-Language Navigation
4. #484 RoboPilot: Generalizable Dynamic Robotic Manipulation with Dual-Thinking Modes
5. #2620 REFLEX: Metacognitive Reasoning for Reflective Zero-Shot Robotic Planning with Large Language Models
6. #2298 Constrained Neuro-Symbolic Framework for Knowledge-Driven Task and Motion Planning
7. #1480 Demonstration-Free Robotic Control Via LLM Agents
8. #268 ICLR: In-Context Imitation Learning with Visual Reasoning
9. #2564 SG-DOR: Learning Scene Graphs with Direction-Conditioned Occlusion Reasoning for Pepper Plants
10. #2619 A Robust Placeability Metric for Model-Free Unified Pick-And-Place Reasoning
11. #3321 GeoReFormer: Geometry-Aware Refinement for Lane Segment Detection and Topology Reasoning
12. #959 SoraNav: Adaptive UAV Task-Centric Navigation Via Zero-Shot VLM Reasoning
13. #4429 Vision-Language Procedural Reasoning for Context-Aware Reward Modeling of Robotic Endovascular Guidewire Navigation
14. #4989 SurgRAW: Multi-Agent Workflow with Chain of Thought Reasoning for Robotic Surgical Video Analysis
15. #837 LOGICWorld: Automated Deep Logic Generation for Interactive Reasoning in Embodied Agents
16. #132 Robotic Long-Horizon Manipulation with Progressive In-Context Code Generation and Episodic Feedback
17. #326 Grounded Vision-Language Interpreter for Long-Horizon Bimanual Task and Motion Planning
18. #2469 Geometric Constraints As General Interfaces for Robot Manipulation
19. #1067 PhaseBot: A Phase-Gated Understanding-Generation-Action Model for Long-Horizon Contact Manipulation
20. #4594 Differentiable SpaTiaL: Symbolic Learning and Reasoning with Geometric Temporal Logic for Manipulation Tasks
21. #1137 AtomTree: A Hierarchical Framework for State-Aware Embodied Instruction Following with LLMs
22. #2690 EmboAlign: Aligning Video Generation with Compositional Constraints for Zero-Shot Manipulation
23. #1413 CognitiveDrone: A VLA Model and Evaluation Benchmark for Real-Time Cognitive Task Solving and Reasoning in UAVs
24. #1208 Incentivizing Multimodal Reasoning in Large Models for Direct Robot Manipulation
25. #3793 CARLA-GS: Decoupling Representation, Reasoning, and Physics Simulation for Autonomous Driving Corner-Case Synthesis
26. #2212 RoBoSR: Structured Scene Representations for Embodied Robotic Reasoning
27. #3240 Test-Time Spatial Reasoning for Robot Manipulation Using Generative Real-to-Sim
28. #1923 VCoT-Grasp: Grasp Foundation Models with Visual Chain-Of-Thought Reasoning for Language-Driven Grasp Generation
29. #311 IndoorR2X: Indoor Robot-To-Everything Coordination with LLM-Driven Planning
30. #430 Physics-Informed Neural Controlled Differential Equations for Scalable Long Horizon Multi-Agent Motion Forecasting
31. #925 PIP-LLM: Integrating PDDL-Integer Programming with LLMs for Coordinating Multi-Robot Teams Using Natural Language
32. #4156 ST-GRL: Spatiotemporal Cognitive Graph Reinforcement Learning for Scalable Multi-Robot Collaborative Exploration
33. #4450 Distilling Collaborative Dynamics into Latent Space for Implicit Coordination in Decentralized Multi-Agent Manipulation
34. #1724 Embodied Chain-Of-Thought Model Via Interleaved Reasoning
35. #947 Articulated-Body Dynamics Network: Dynamics-Grounded Prior for Robot Learning
36. #1246 ViSA-Enhanced Aerial VLN: A Visual-Spatial Reasoning Framework for Aerial Vision-Language Navigation
37. #1383 Don't Fool Me Twice: Adapting to Adversity in the Wild with Experience-Driven Reasoning
38. #5060 WeldLLM: A Multimodal Framework for Welding Defect Detection and Automated Diagnostic Reasoning
39. #2143 A Collaborative Reasoning Framework for Anomaly Diagnostics in Underwater Robotics
40. #2265 Hybrid Chain-Of-Thought Reasoning for Vision–Language–Action Models
41. #2691 Splatting As Attention: Reasoning in 3D Gaussian Fields for Occupancy Prediction in Autonomous Driving
42. #1811 DialogVLA: Bridging Reasoning Action in Bimanual Manipulation Via Parallel Mixture-Of-Experts
43. #2500 DualCoT-VLA: Visual-Linguistic Chain of Thought Via Parallel Reasoning for Vision-Language-Action Models
44. #3831 3D Scene Graph Prediction: Generating Hierarchical Models from Partially Observed Environments
45. #1324 From Pixels to Concepts: Growing Rich 3D Semantic Scene Graph Forests Utilizing Foundation Models
46. #1006 HyProSG: A Hyperbolic Prototype Network for Hierarchical 3D Scene Graph Generation
47. #2448 TerraAlign: Language-Supervised Alignment of Vision and Proprioception for Multi-Grained Terrain Classification
48. #4772 STaR: Scalable Task-Conditioned Retrieval for Long-Horizon Multimodal Robot Memory
49. #553 3D UAV Trajectory Estimation and Classification from Internet Videos Via Language Model
50. #2133 DeNoise2Completion: Diffusion-Based Unified Model for Point Cloud Denoising and Completion
51. #385 Scene-Q: Confidence-Aware Coarse-To-Fine Querying of 3D Scenes with Selective VLM Reasoning
52. #725 FailSafe: Reasoning and Recovery from Failures in Vision-Language-Action Models
53. #1122 TacReasoner: A Dynamic Tactile-Language Framework for Interactive Reasoning in Real-World Scenarios
54. #4453 Perception-Aware Multimodal Spatial Reasoning from Monocular Images
55. #450 Closing the Navigation Compliance Gap in End-To-End Autonomous Driving
56. #1420 Driver-State-Aware Risk Assessment and Driving Assistance Based on an End-To-End Model
57. #3528 HiD2: A Trajectory Generator for High-Density Traffic and Diverse Agent-Interaction Scenarios
58. #650 Chat2Scenic: An Iterative RAG-Based Framework for Scenario Generation in Autonomous Driving
59. #2464 Super Agents and Confounders: Influence of Surrounding Agents on Vehicle Trajectory Prediction
60. #1249 Unified Early Traffic Conflict Detection for Autonomous Vehicles Via Future Trajectory Prediction
61. #638 PEDRA: PErsonalized Driving Representation for Autonomy
62. #1666 CORAL: COntextual Reasoning and Local Planning in A Hierarchical VLM Framework for Underwater Monitoring
63. #317 DiffAttn: Diffusion-Based Drivers' Visual Attention Prediction with LLM-Enhanced Semantic Reasoning
64. #1835 Frontier-as-Token: Structured Spatial Reasoning for Zero-shot Object Navigation

## 출처

- IROS 2026 Paper & Author Index 기반 검색 결과
- 프로그램 규모: 1,933편
- 검색어: `reasoni`
- 검색 결과 생성일: 2026-08-26
