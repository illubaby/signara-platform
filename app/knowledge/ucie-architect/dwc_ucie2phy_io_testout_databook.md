**UCIe**** ****2****.0 ****PHY ****Testout ****Analog ****Hard Macro**

Databook

**Library: dwc_****ucie2phy****_****testout **

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
| **Dec 29, 2025** | Tri Vo | 0.71 | Change AnaIn* related power to VDD () |
| **Oct 24, 2025** | Tri Vo | 0.7 | Update top diagram. Add PAD_DigOut voltage sense point and resistor to enhance ESD Add section for ESD connection Add section for TX impedance measurement Remove VPH |
| **Aug 05, 2025** | Tri Vo | 0.61 | Update block diagram and truth table 3-4 () |
| **Jul 19, 2025** | Tri Vo | 0.6 | Change PAD_AnalogOut power domain from VPH to VDD to support non-IO device technode () |
| **May 10, 2025** | Tri Vo | 0.55 | Change pin AnaIn[5:0] to AnaIn0, AnaIn1…,AnaIn5. Update related power domain for them. |
| **Apr 11, 2024** | Tri Vo | 0.5 | Change cell name following the new conventional name rule (support UCIe-A/S, NS/EW PHY orientation Support div4 () Change AnaIn[5:0] power domain from VDD to VPH |
| **Sep 05, 2024** | Tri Vo | 0.4 | Add new power VPH Add section for Analog test input description |
| **Jun 26, 2024** | Tri Vo | 0.3 | Update block diagram AnalogTstMode[1:0] to AnalogTstMode[2:0] to support more analog input Rename AnalogIn to AnaIn[5:0] Remove VrefIn |
| **May 09, 2024** | Chinh Ngo | 0.2 | Change bit width TxCal from 7 bits to 6 bits |
| **Feb**** ****29****, 202****4** | Tri Vo | 0.1 | Clone from UCIe gen1 Change prefix uciephy to ucie2phy |

# Introduction

This macro is used for sending the test signal out on the BP_M_TEST bump. The purpose of this macro is also to meet the require drive strength at PAD_DigOut and ESD.

# Operating Conditions

## RECOMMENDED OPERATING CONDITIONS

Table 21: Recommended operating conditions for IO

| **Parameter** | **Description** | **Min** | **Typ** | **Max** | **Unit** |
| --- | --- | --- | --- | --- | --- |
| VCCIO | Driver supply Voltage (normal mode) | 0.45 | 0.50 | 0.55 | V |
| VDD | Core supply Voltage (normal mode) | 0.675 | 0.75 | 0.825 | V |
| VCCAON | Always on Auxiliary Supply | 0.675 | 0.75 | 0.825 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | oC |

Table 22: Support frequencies

| **Function** | **Frequency** |
| --- | --- |
| **d****wc_****ucie2phy****_t****estout** | 10GHz @1.6pF loading |

Table 23: Timing specification

| **Parameter** | **Min** | **Typ** | **Max** | **Unit** |
| --- | --- | --- | --- | --- |
| Clock input min pulse width | 25 | - | - | ps |

## LIBRARY CHARACTERIZATION CORNERS

Table 24: Corners for library characterization

| **Process** | **Core Voltage (V)** | **Temperature (C)** | **RC Corner** |
| --- | --- | --- | --- |
| SSG | 0.675 | -40 | typical |
| SSG | 0.675 | 125 | typical |
| FFG | 0.825 | -40 | typical |
| FFG | 0.825 | 125 | typical |
| SSG | 0.675 | 0 | typical |
| FFG | 0.825 | 0 | typical |
| TT | 0.75 | 25 | typical |

# dwc_ucie2phy_testout

## FEATURES

- Two output PADs:
- One for digital output (from 2 dwc_ucie2phy_tximp) to observe PLL frequency, Maximum operating frequency: 10.0 GHz, support divider by 2 and by 4.
- One for analog output to observe PLL/Bandgap/POR/VREG analog signals, internal Vref and VDD monitor
- Output Impedance: 25Ohm for UCIe-A and 30Ohm for UCIe-S
- When two TXs are enabled, the output current is double.
- Driver currents are calibrated by Calibration buffer
- Ansychronous TxDat and TxEn
- 2kV HBM, 6A CDM ESD tolerant
Table 31 Testout cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_testout_a_ns | Support UCIe-A, NS PHY orientation |
| **2** | dwc_ucie2phy_testout_a_ew | Support UCIe-A, EW PHY orientation |
| **3** | dwc_ucie2phy_testout_s_ns | Support UCIe-S, NS PHY orientation |
| **4** | dwc_ucie2phy_testout_s_ew | Support UCIe-S, EW PHY orientation |

## PINS DESCRIPTION

Table 32: Single ended output buffer Pin Description

| **Pin** | **Direction** | **Type** | **Domain** | **Description** |
| --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | Core supply |
| VCCIO | Input | Power | VCCIO | IO supply |
| VCCAON | Input | Power | VCCAON | 0.75V IO supply |
| VSS | Input | Ground | VSS | Common ground |
| PwrOk_VAON | Input | Digital | VCCAON | Tells the macro if the supplies are valid |
| TestoutCalN[5:0] | Input | Digital | VDD | Calibration bits for Testout pulldown |
| TestoutCalP[5:0] | Input | Digital | VDD | Calibration bits for Testout pullup |
| OutputConfig[1:0] | Input | Digital | VDD | Output configuration when the supplies are valid |
| drvConfig | Input | Digital | VDD | Driver configuration (to enable a single Tx for characterization purposes) (see section 2.3) |
| DigitalIn | Input | Digital | VDD | Digital data to observe |
| PAD_DigOut | Output | Digital | VCCIO | Digital data output, connect to bump |
| TestoutDivEn | Input | Digital | VDD | Enable frequency divider |
| TestoutResetn | Input | Digital | VDD | Asynchronous reset pin for Flipflop in frequency divider, active low |
| AnaIn0 | Inout | Analog | VDD | Analog input |
| AnaIn1 | Inout | Analog | VDD | Analog input |
| AnaIn2 | Inout | Analog | VDD | Analog input |
| AnaIn3 | Inout | Analog | VDD | Analog input |
| AnaIn4 | Inout | Analog | VDD | Analog input |
| AnaIn5 | Inout | Analog | VDD | Analog input |
| PAD_AnalogOut | Inout | Analog | VDD | Analog inout, connect to bump |
| AnalogTstMode[2:0] | Input | Digital | VDD | Select analog output. See Table 33 |
| Reserved[6:0] | Input | Digital | VDD | Reserved for future use |

## FUNCTIONAL BLOCK DIAGRAM

High level block diagram of **dwc_****ucie2phy****_testout** is described in Figure 31. This cell can be split into two parts: Analog output and digital output.

Analog output is used to monitor the internal analog signal: referent voltage, PLL analog test out, or internal core voltage. User also can use this analog port to input the external referent voltage. The input voltage range is from 0 to VDD.

Digital output is used to monitor the internal digital signal like PLL output clock. User also can use to measure the DC parameters of TX like VOH/VOL

Figure 31 Block diagram of testout

## TRUTH TABLES

### Analog output

Table 33: Analog output decode table

| **PwrOk_VAON** | **AnalogTstMode****[****2****]** | **AnalogTstMode****[1]** | **AnalogTstMode****[0]** | **PAD_AnalogOut** |
| --- | --- | --- | --- | --- |
| 0 | X | X | X | High Z |
| 1 | 0 | 0 | 0 | Local VDD level |
| 1 | 0 | 0 | 1 | PAD_DigOut |
| 1 | 0 | 1 | 0 | AnalogIn0 |
| 1 | 0 | 1 | 1 | AnalogIn1 |
| 1 | 1 | 0 | 0 | AnalogIn2 |
| 1 | 1 | 0 | 1 | AnalogIn3 |
| 1 | 1 | 1 | 0 | AnalogIn4 |
| 1 | 1 | 1 | 1 | AnalogIn5 |

**Note**: x = don’t care

### Digital output

Table 34: Digital output decode table

| **PwrOk_VAON** | **OutputConfig****[1]** | **OutputConfig****[0]** | **drvConfig** | **TestoutDiv** **En** | **PAD_DigOut** |
| --- | --- | --- | --- | --- | --- |
| 0 | X | X | X | X | HiZ |
| 1 | 0 | 0 | X | X | HiZ |
| 1 | 0 | 1 | 0/1 | 0 | DigitalIn (*) |
| 1 | 1 | 0 | 0/1 | 0 | DigitalIn (*) |
| 1 | 0 | 1 | 0/1 | 1 | DigitalIn is divided by 2 (*) |
| 1 | 1 | 0 | 0/1 | 1 | DigitalIn is divided by 4 (*) |
| 1 | 1 | 1 | X | X | HiZ |

**Note: **

X = don’t care

(*) drvConfig = 0, both TX drivers are enabled

drvConfig = 1, one TX drivers is enabled

### RTL AND TIMING REQUIREMENTS

#### DFT

Table 35 DFT input condition

| Pin | Value |
| --- | --- |
| OutputConfig[1:0] | 2’b0 |
| AnalogTstMode[2:0] | 3’b0 |

#### IDDQ measurement

| Pin | Value |
| --- | --- |
| OutputConfig[1:0] | 2’b0 |
| AnalogTstMode[2:0] | 3’b0 |
| DigitalIn | 0 |

#### Burn-in recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run mission mode.

## Analog test input

The below table describes the connection of AnaIn0 AnaIn5

| **Pin** | **Connection** |
| --- | --- |
| AnaIn0 | PLL analog testout port |
| AnaIn1 | RXCKTRK/RxVrefOut |
| AnaIn2 | Bandgap/vbg |
| AnaIn3 | Por/RxVbias |
| AnaIn4 | Por/PgenIrefOut[0] |
| AnaIn5 | DWord Vreg analog testout port |

## Implementation guideline for ESD

To meet 6A CDM ESD requirement, it is a must to add small resistor (5-6ohm) in between PAD_DigOut first ESD and TXIMP. This resistor combines with ESD inside TXIMP to form a second ESD circuit.

Below is general instruction:

Figure 32 Guideline for PAD_DigOut ESD enhancement

## TX impedance measurement sequence

Because of additional resistance for ESD enhancement, the TX impedance measurement must follow the following sequence:

- Enable one and only one TXIMP
- Program ZCALP/N code.
- Configure AnalogTstMode[2:0] = 3’b001
- Configure the TXIMP data 1 or 0 to measure pull-up or pull-down impedance.
- Connect PAD_DigOut to external voltage source (V1). Slowly sweep voltage V1 from 0 to VCCIO level.
- Monitor voltage at PAD_AnalogOut. When PAD_AnalogOut equals the target threshold (1/2*VCCIO or 5/16*VCCIO), measure the sink (or source) current (I1) through V1.
- TX impedance is calculated be equation:
- Or
## Simulation Plan

| No | Testbench | Description |
| --- | --- | --- |
| **1** | tb_testout_tran_post.bbSim | Transient simulation, check function and performance |
| **2** | tb_testout_pwrsqn_post.bbSim | Power sequence sim |
| **3** | tx_top_vccio_rc_post.bbSim | Measure Rdie-Cdie VCCIO |
| **4** | tx_top_vccaon_rc_post.bbSim | Measure Rdie-Cdie VCCAON |
| **5** | tx_top_vdd_rc_post.bbSim | Measure Rdie-Cdie VDD |
| **6** | tx_top_func_post.bbSim | Cross functional check spice vs verilog |
| **7** | tx_top_dcck_post.bbSim | Dynamic CCK |
| **8** | tx_top_emir.bbSim | EMIR check |
