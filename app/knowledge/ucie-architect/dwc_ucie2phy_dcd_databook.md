**UCIe****2**** ****PHY ****Duty Cycle Detector ****Analog Hard****-****Macro**

Databook

UCIe2 Standard/Advance

Copyright Notice and Proprietary Information Notice

Copyright © 2025 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

Destination Control Statement

All technical data contained in this publication is subject to the export control laws of the United States of America. Disclosure to nationals of other countries contrary to United States law is prohibited. It is the reader's responsibility to determine the applicable regulations and to comply with them.

Disclaimer

SYNOPSYS, INC., AND ITS LICENSORS MAKE NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS MATERIAL, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Trademarks

Synopsys and certain Synopsys product names are trademarks of Synopsys, as set forth at

All other product or company names may be trademarks of their respective owners.

Synopsys, Inc.690 E. Middlefield RoadMountain View, CA 94043

# Revision History

| Date | Owner | Revision | Description |
| --- | --- | --- | --- |
| **May**** ****07****, 202****4** | Tri Vo | 0.1 | Cloned from UCIe gen1 Changed cell name from dwc_uciephy_dcd to dwc_ucie2phy_dcd |
| **Jun 06, 2024** | Huy Pham | 0.2 | Update Figure 31 High level architecture: add VDDREG domain & level shifter at output control signals Update Table 32: Pin Description: add pin VDDREG to support both VDD domain in WRITE clock tree & VDDREG domain in READ clock tree Add Iddq/Burn-in test recommendation |
| **Sep 20, 2024** | Tri Vo | 0.3 | Support I/Q phase detector () Increase dcd_mode to [2:0] Update input clock: clk_inp0/1 and clk_inn0/1 |
| **Oct 08, 2024** | Tri Vo | 0.4 | New cell dwc_ucie2phy_txdcd |
| **Nov 01, 2024** | Chinh Ngo | 0.5 | Remove L2H in dcdtx because the VCCIO supply is only 0.45V |
| **Apr 11, 2024** | Tri Vo | 0.6 | Change cell name to follow new conventional name (UCIe-A/S and PHY orientation) Change cell name *_txdcd to *_dcdtx |
| **May 09, 2024** | Tri Vo | 0.61 | Remove _a/s in dwc_ucie2phy_dcd |
| **Nov 17, 2024** | Tri Vo | 0.7 | Remove VCCIO (no longer support PAD duty cycle sense) |

# Introduction

Duty cycle detector (DCD) circuit is used to detect duty cycle error with a single output bit. The circuit design is based on a fully differential comparator (with offset calibration) that is used to compare the average DC value of two input clocks (differential mode) or compare the average DC value of one input clock with an internally generated reference voltage (single ended mode). The output of this circuit is then used by DCA (duty cycle adjustment) to correct the duty cycle.

# Operating Conditions

## RECOMMENDED OPERATING CONDITIONS

Table 21: Recommended operating conditions

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VDD | Core supply Voltage | 0.66 | 0.75/0.85 | 0.935 | V |
| VDDREG | Regulator Voltage | 0.66 | 0.75/0.85 | 0.935 | V |
| VCCIO | IO supply, 0.5v mode | 0.45 | 0.50 | 0.55 | V |
|  | IO supply, overdrive mode | 0.66 | 0.75/0.85 | 0.935 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | C |

Table 22: Support frequencies

| **Function** | **Frequency** |
| --- | --- |
| dwc_ucie2phy_dcd_* | clk_inp/clk_inn: 10GHz clk_sample: 2.5GHz |

# dwc_ucie2phy_dcd_*

## FEATURES

- Support two clock sense option:
- Differential clock sense.
- Single ended clock sense.
- dcd_out is sampled with the rising edge of the clk_sample
- The analog DCD ideally should be placed close to the end of the clocking path.
## CELL LIST

Cell list is shown in Table 31. They have the same function and pin interface.

Table 31 Cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_dcd_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_dcd_ew | Support UCIe-A/S, EW PHY orientation |

## PINS DESCRIPTION

Table 32: Pin Description

| **Pin** | **Direction** | **Type** | **Power ****Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| dcd_mode[2:0] | Input | Digital | VDD | DFI clk | Select DCD operation mode. Refer to Table 33 |
| offset[5:0] | Input | Digital | VDD | DFI clk | Input code for comparator offset compensation. Default code is 6’b000000 |
| clk_inp0 | Input | Digital | VDDREG | pclk | Input clock to be sensed duty cycle |
| clk_inp1 | Input | Digital | VDDREG | pclk | Input clock to be sensed duty cycle |
| clk_inn0 | Input | Digital | VDDREG | pclk | Input clock to be sensed duty cycle |
| clk_inn1 | Input | Digital | VDDREG | pclk | Input clock to be sensed duty cycle |
| clk_sample | Input | Digital | VDD | DFI clk | Sampling clock for the comparator |
| dcd_out | Output | Digital | VDD | DFI clk | Comparator output |
| reserve[2:0] | Input | Digital | VDD | DFI clk | Reserved pins |
| VDDREG | Input | Power | VDDREG |  | Vreg supply |
| VDD | Input | Power | VDD |  | Core supply |
| VSS | Input | Ground | VSS |  | Ground |

## FUNCTIONAL BLOCK DIAGRAM

The macro contains:

- The digital control logic.
- The analog core, including a mux for the two input clocks, two RC tanks, pre-amplifier and comparator.
The RC tank is a low pass filter. Its output value is the average DC level of the input clock.

Vref generator is a voltage divider. The value of Vref is VDDREG/2

The analog Mux0 and Mux1 are used to select the clock sense mode. Transmission gate M3 is used to short outp_avg and outn_avg together in the offset calibration and power down mode.

The path from “clk_inp* to outp_avg”, “clk_inn* to outn_avg” and “vref* to outn_avg” are matched to minimize the noise effect.

Two NXOR gates are used to combine clk_inp* and clk_inn* into new clock ckp and ckn.

VDDREG domain is to support both VDD (in WRITE clock tree) & VDDREG (in READ clock tree). Therefore, it also needs to have level shifter at output logic control signals.

Figure 31 High level architecture

### Operation Modes

- **Powerdown mode**: the analog dcd is not measuring the incoming clock signals. The pre-amplification is put into power down mode and the comparator is in the precharge mode. The two RC tank outputs are weakly driven to VSS by selecting the weak tie low on Mux0 and enable the transmission gate M3. User is recommended to put the DCD into power down mode whenever it is unused.
- **Offset calibration mode**: The offset code is incremented one by one to check when the comparator output toggles. The offset code is then stored and applied for the mission mode.
- **Mission mode**:
- Differential clock sense. The average DC level of clk_inp*/ckp and clk_inn*/ckn is compared together (refer to Table 33). DCD generates “0” on dcd_out when the DC level of clk_inp* or ckp is less than the DC level of clk_inn* or ckn. DCD generates “1” on dcd_out when the DC level of clk_inp* or ckp is larger than the DC level of clk_inn* or ckn. ***This mode is recommended ******for sensing the****** Dwork****** ******READ****** clock****** tree*** which two output clocks from output RXCK are connected to clk_inp* and clk_inn* respectively.Any unused clock input, user is recommended to tie them to ground.
- Single ended clock sense: The average DC level of clk_inp0 and the internal vref is compared together. DCD generates “0” on dcd_out when the DC level of clk_inp0 is less than the Vref. DCD generates “1” on dcd_out when the DC level of clk_inp0 is larger than Vref. Other clock inputs are unused in this mode. Any unused clock input, user is recommended to tie them to ground.
- ***This mode is recommended for sensing the Dwork ******WRITE****** clock****** tree*** which the input clock of LCDL is connected to clk_inp0.
Table 33 Truth table dcd_mode

| **Input** | **Output** | **Description** |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **dcd_mode[2]** | **dcd_mode[1]** | **dcd_mode[0]** | **outp** | **outn** |  |
| 0 | 0 | 0 | Weak 0 | Weak 0 | Power down mode |
| 0 | 0 | 1 | Vref | Vref | Offset calibration mode |
| 0 | 1 | 0 | clk_inp0 | Vref | Mission mode, single ended clock sense |
| 0 | 1 | 1 | clk_inp0 | clk_inn0 | Mission mode, differential clock sense |
| 1 | 0 | 0 | clk_inp1 | clk_inn1 | Mission mode, differential clock sense |
| 1 | 0 | 1 | ckp | ckn | Mission mode, differential clock sense |
| 1 | 1 | 0 | Weak 0 | Weak 0 | Reserved |
| 1 | 1 | 1 | Weak 0 | Weak 0 | Reserved |

### Special configurations

#### Quadrature Clock Input

For I/Q calibration purpose, user can provide 4-phase clock and set dcd_mode to 3’b101. Two internal NOXR gate convert these clocks to two differential clocks with double frequency. By monitoring the dcd_out, user can know I/Q phase mismatch.

Figure 32 Operation waveform of quadrature clock

#### VDDREG Usage

Cell dwc_ucie2phy_dcd is placed at different locations (TX & RX region), so the power supply assigned to VDDREG must be followed Table 3-3 below:

Table 34 Special configuration of dwc_ucie2phy_dcd

| **Location** | **VDDREG ** |
| --- | --- |
| TX region – WRITE clock tree | VDD |
| RX region – READ clock tree | VDD_REG (output Vreg) |

# dwc_ucie2phy_dcdtx_*

## FEATURES

dwc_ucie2phy_dcdtx is a stripped-down version of dwc_ucie2phy_dcd that aims for the transmitter IO clock calibration. The feature is almost the same, except it only supports single ended clock mode and with only two input clocks.

In DW level, two transmitter IOs share one DCD cell which the clock sense point is connected to clk_in0 and clk_in1.

## Cell list

Cell list is shown in Table 41. They have the same function and pin interface.

Table 41 Cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_dcdtx_a_ns | Support UCIe-A, NS PHY orientation |
| **2** | dwc_ucie2phy_dcdtx_a_ew | Support UCIe-A, EW PHY orientation |
| **3** | dwc_ucie2phy_dcdtx_s_ns | Support UCIe-S, NS PHY orientation |
| **4** | dwc_ucie2phy_dcdtx_s_ew | Support UCIe-S, EW PHY orientation |

## PINS DESCRIPTION

Table 42: Pin Description

| **Pin** | **Direction** | **Type** | **Power ****Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| dcd_mode[1:0] | Input | Digital | VDD | DFI clk | Select DCD operation mode. Refer to Table 43 |
| offset[5:0] | Input | Digital | VDD | DFI clk | Input code for comparator offset compensation. Default code is 6’b000000 |
| clk_in0 | Input | Digital | VDD | pclk | Input clock to be sensed duty cycle |
| clk_in1 | Input | Digital | VDD | pclk | Input clock to be sensed duty cycle |
| clk_sample | Input | Digital | VDD | DFI clk | Sampling clock for the comparator |
| dcd_out | Output | Digital | VDD | DFI clk | Comparator output |
| reserve[2:0] | Input | Digital | VDD | DFI clk | Reserved pins |
| VDD | Input | Power | VDD |  | Core supply |
| VSS | Input | Ground | VSS |  | Ground |

## FUNCTIONAL BLOCK DIAGRAM

Refer to 3.4 for more information.

Figure 41 High level architecture

### Operation Modes

- **Power**** ****down mode**: the analog dcd does not measure the incoming clock signals. The pre-amplification is put into power down mode and the comparator is in the pre charge mode. The two RC tank outputs are weakly driven to VSS by selecting the weak tie low on Mux1 and enable the transmission gate M3. User is recommended to put the DCD into power down mode whenever it is unused. **The dcd_out is ****forced**** to zero in this mode.**
- **Offset calibration mode**: The offset code is incremented one by one to check when the comparator output toggles. The offset code is then stored and applied for the mission mode.
- **Mission mode**: The average DC level of clk_in0 (or clk_in1) and the internal vref is compared together. DCD generates “0” on dcd_out when the DC level of clk_in0 (or clk_in1) is less than the Vref. DCD generates “1” on dcd_out when the DC level of clk_in0 is larger than Vref. Any unused clock input, user is recommended to tie them to ground.
Table 43 Truth table dcd_mode

| **Input** | **Output** | **Description** |  |  |
| --- | --- | --- | --- | --- |
| **dcd_mode[1]** | **dcd_mode[0]** | **outp** | **outn** |  |
| 0 | 0 | Weak 0 | Weak 0 | Power down mode |
| 0 | 1 | Vref | Vref | Offset calibration mode |
| 1 | 0 | clk_in0 | Vref | Mission mode, sense clk_in0 |
| 1 | 1 | clk_in1 | Vref | Mission mode, sense clk_in1 |

### Recommended Connection

Figure 42 Recommended connection between tx and dcdtx

# DESIGN CONSTRAINT

This section is applicable for both dwc_ucie2phy_dcd and dwc_ucie2phy_dcdtx

## RTL AND TIMING REQUIREMENTS

Table 51 RTL and timing requirements

| **Parameter** | **Symbol** | **Value** | **Unit** | **Note** |
| --- | --- | --- | --- | --- |
| Settling Time | DCDOffsetSettleInitial DCDMissionSettleInitial | 100 | ns |  |
| Comparator sample time in offset calibration mode | DCDOffsetSampleTime | 100 | ns |  |
| Comparator sample time in mission mode | DCDMissionSampleTime | 100 | ns |  |

### Settling time for mission mode and calibration mode

A minimum wait time (DCDOffsetSettleInitial/DCDMissionSettleInitial - Table 51) is needed when enter the mission mode or calibration mode, so that the key analog signals are ready to be sampled by the Sense-Amp. These changes can happen due to the following scenarios:

- Power ramp up done to Mission mode or Offset calibration mode
- Power down mode to Mission mode or Offset calibration mode
- Mission mode to Offset calibration mode
- Offset calibration mode to Mission mode
So, this wait time needs to be observed from all of the above events (from whichever happens latest if they are in sequence) to the first valid sampling edge of dwc_ucie2phy_dcd/clk_sample.

Figure 51 Settling time in Mission mode

Figure 52 Settling time in Offset calibration mode

### Sample Time in Comparator Offset Calibration Mode

In offset calibration mode, a minimum wait time (DCDOffsetSampleTime - Table 51) is needed when change one offset code to another offset code, so that the key analog signals are ready to be sampled by the Sense-Amp.

Figure 53 Sample time in comparator offset calibration mode

### Sample Time in Mission mode

In mission mode, a minimum wait time (DCDMissionSampleTime - Table 51) is needed when any change in clock duty cycle at pin dwc_ucie2phy_dcd/clk_in, so that the key analog signals are ready to be sampled by the Sense-Amp.

Figure 54 Sample time in Mission mode

### DFT Requirement

During scan mode, user need to configure the operation mode to power down by setting the dcd_mode[1:0] to 2’b00

### Iddq Measurement

Table 52 Setting for IDDQ measurement

| Pin | Value | Description |
| --- | --- | --- |
| dcd_mode | 2’b00 | Power down |

### Burn-in Test Recommendations

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run in mission mode.

User needs to keep VDDREG level same as VDD core. To do this, voltage regulator is configured in bypass mode.

## TRAINING PROCEDURES

**Offset calibration routine:**

1. Enable Comparator by setting csrPclkDCDEn = 1.

2. Put DCD circuit into offset mode, csrDCDOffsetMode = 1.

3. Wait DCDOffsetSettleInitial

4. Set csrDCDOffset to {min value} (-31)

5. Foreach csrDCDOffset, wait DCDOffsetSampleTime, then sample DCDOut by 1 cycle of SampleClk, wait for 2 DFICLK cycles.

6. If DCDOut == 1, stop; else increment csrDCDOffset and Goto step 5

7. Record csrDCDOffset as MinMaxOffset

8. Set csrDCDOffset to {max value} (+31)

9. Foreach csrDCDOffset, wait DCDOffsetSampleTime, then sample DCDOut by 1 cycle of SampleClk, wait for 2 DFKCLK cycles

10. If DCDOut == 0, stop; else decrement csrDCDOffset and Goto step 9

11. Record csrDCDOffset as MaxMinOffset

12. Take the average of MinMaxOffset and MaxMinOffset and set as the final csrDCDOffset value. (note: offset value is a signed binary code)

13. If MinMaxOffset or MaxMinOffset equals to max or min values, set a saturation flag to CSR for readout.

General considerations:

- SampleClk is a gated DFICLK.
- csrDCDOffset should be programmable between min and max code. It is either generated by the state-machine or can be overwritten by users.
- csrDCDOffset sweeping can’t be wrapped around. It’s stopped at min or max value.
- CSR default for the offset should be equivalent to no offset in the comparator.
- The state-machine should be in the DFICLK domain. No CDC issue because both SampleClk and DCDOut are in DFICLK domain.
- csrDCDOffset code: 6-bit binary code, MSB is the signed bit (1 is negative)
- default and reset value are: 6’b00000 this is the state of no offset.
- min value: -31 (6’b111111)
- max value: +31 (6’b011111)
## ELECTRICAL SPECIFICATION

Table 53 Electrical specification

| Parameter | Min | Typ | Max | Unit | Note |
| --- | --- | --- | --- | --- | --- |
| DC gain | 20 |  |  | Db |  |
| Phase margin | 50 |  |  | Deg | (±4.5 sigma) |
| Output common mode voltage | 250 |  |  | mV | (±4.5 sigma) |
| Comparator resolution | -20 |  | 20 | mV | (±3 sigma) |
| Comparator offset after 10 years | -2 |  | 2 | mV |  |
| Referent voltage | 49.5 |  | 50.5 | mV | (100*vref/VDD) |
| Average voltage of clkinn after RC filter | 47 |  | 53 | mV | (100*avg_clkn/VDD) |
| Average voltage of clkinp after RC filter | 47 |  | 53 | mV | (100*avg_clkp/VDD) |
| P2p ripple voltage of clk_inp after RC filtter |  |  | 2 | mV |  |
| P2p ripple voltage of vref after RC filter |  |  | 2 |  |  |
| Duty cycle due to buffer and RC filter in single-ended clock mode | -2.5 |  | 2.5 | % | 10GHz input clock |
| Duty cycle due to buffer and RC filter in differential clock mode | -1 |  | 1 | % | 10GHz input clock |
| Duty cycle error after canceling comparator offset | -0.5 |  | 0.5 | % | 10GHz input clock |
| Total duty cycle error, single ended clock mode | -3 |  | 3 | % | 10GHz input clock |
| Total duty cycle error, differential clock mode | -1.5 |  | 1.5 | % | 10GHz input clock |
| Kickback diffmax bw avg_clkp and vref | -2 |  | 2 | mV |  |
| Kickback diffmin bw avg_clkp and vref | -2 |  | 2 | mV |  |
| Offset compensate range min | 15 |  |  | mV |  |
| Offset compensate range max |  |  | 15 | mV |  |
| Offset step max |  |  | 2 | mV |  |
| Offset step avg |  |  | 2 | mV |  |
| Offset post correction | -2.25 |  | 2.25 | mV |  |
| Tsettling1 (normal) |  |  | 50 | mV |  |
| Tsettling2 (mission) |  |  | 20 | mV |  |
| Tsettling3 (calibration) |  |  | 50 | mV |  |
| Tsettling4 (calibration) |  |  | 20 | mV |  |
| Comparator offset MC simulation – bidirectional, post correction |  |  | 3.3 | mV | Sweep the input voltage in both directions |
| Mission mode power |  | TBD |  | uA | Typical condition |
| Offset calibration mode power |  | TBD |  | uA | Typical condition |
| Power down |  | TBD |  | uA | Typical condition |
| DCD_error_vdrift | -0.5 |  | 0.5 | % | DCD error vs Voltage drift. Keep same offset code, vary voltage from min to max. Measure offset voltage and DCD error. |
| DCD_error_Tdrift | -0.5 |  | 0.5 |  | DCD error vs Temp drift​. Keep same offset code, vary temp from -40 to 125. Measure offset voltage and DCD error |

## Rdie-Cdie (TBU)

Figure 55 Rdie-Cdie model

Table 54 Rdie and Cdie value of VDD domain

| Corner | Rdie_0 (kOhm) | Rdie_1 (mOhm) | Cdie_1 (pF) | Rdie_2 (Ohm) | Cdie_2 (pF) |
| --- | --- | --- | --- | --- | --- |
| TT | 431.088 | 10603.3 | 0.36909 | 1389.5 | 0.0416805 |
| FFG | 1331.96 | 9319.73 | 0.360101 | 1237.75 | 0.0387982 |
| SSG | 65.0465 | 11919 | 0.376094 | 1111.13 | 0.0667362 |

## EMIR condition (TBU)

Figure 56 EMIR verification condition

| **Parameter** | **EM (*)** | **IR** |  |
| --- | --- | --- | --- |
| Process | FF | FF | SS |
| Voltage supply | Vtyp + 10% for VDD | Vtyp + 10% for VDD | Vtyp – 10% for VDD |
| Temperature | 105C with self heat | 105C | -40C |
| RC extraction | Typical with temperature sensitivity | Typical with temperature sensitivity | Typical with temperature sensitivity |
| Operation mode | Mission mode and offset calibration mode, max frequency | Mission mode and offset calibration mode, max frequency | Mission mode and offset calibration mode, max frequency |
| Time step (ratau) | 3ps | 3ps | 3ps |
| Pass condition | <1 (iavg, irms, acpc) | <15mV for each (VDD-VSS) | <15mV for each (VDD-VSS) |

## TESTBENCHES

TBU
