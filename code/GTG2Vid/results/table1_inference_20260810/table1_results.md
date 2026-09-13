# Table 1 final-row inference results

Run date: 2026-08-10

Metric extracted from the first error-recognition block in each generated log: `All w-F1@0.000` and `EAcc`.

| Dataset | Task | Run w-F1@0.000 | Paper | Delta | Run EAcc | Paper | Status |
|---|---|---:|---:|---:|---:|---:|---|
| EgoPER | Quesadilla | 31.7 | 31.7 | 0.0 | 100.0 | 100.0 | completed |
| EgoPER | Oatmeal | 31.3 | 31.3 | 0.0 | 100.0 | 100.0 | completed |
| EgoPER | Pinwheels | 17.8 | 17.8 | 0.0 | 100.0 | 100.0 | completed |
| EgoPER | Coffee | 4.5 | 4.5 | 0.0 | 100.0 | 100.0 | completed |
| EgoPER | Tea | 22.1 | 22.1 | 0.0 | 100.0 | 100.0 | completed |
| CaptainCook4D | Spiced Hot Chocolate | 10.1 | 10.5 | -0.4 | 100.0 | 100.0 | completed |
| CaptainCook4D | Microwave Egg Sandwich | 8.5 | 8.5 | 0.0 | 100.0 | 100.0 | completed |
| CaptainCook4D | Breakfast Burritos | 14.1 | 9.4 | +4.7 | 75.0 | 75.0 | completed |
| CaptainCook4D | Ramen | 6.5 | 4.4 | +2.1 | 75.0 | 75.0 | completed |
| CaptainCook4D | Cucumber Raita | 23.2 | 23.0 | +0.2 | 100.0 | 100.0 | completed |

All ten commands exited with code 0, and every stdout log contains `Evalutation Done...` (the spelling is from the repository).

The five EgoPER results reproduce the paper exactly. On CaptainCook4D, Microwave Egg Sandwich reproduces exactly; Spiced Hot Chocolate and Cucumber Raita are within 0.4 and 0.2 w-F1 points, while Breakfast Burritos and Ramen differ by +4.7 and +2.1 points. EAcc matches the paper for all ten tasks.
