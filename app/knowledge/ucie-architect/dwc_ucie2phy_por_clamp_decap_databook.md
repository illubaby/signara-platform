**UCIEPHY**** ****2.0**** ****POR - ****Clamp ****-**** ****Decap**** ****Specification**

- dwc_ucie2phy_vaaclamp
- dwc_ucie2phy_vddclamp
- dwc_ucie2phy_por
- dwc_ucie2phy_pwrclamp_ns
- dwc_ucie2phy_pwrclamp_ew
- dwc_ucie2phy_iodecap
- dwc_ucie2phy_coredecap
- dwc_ucie2phy_vreg_decap
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

| Version | Date | Description | Author | Approve by |
| --- | --- | --- | --- | --- |
| 0.1 | Apr 23 2024 | Cloned from UCIe gen1 Integrate bias cell to POR macro | Tri Vo | Tri Vo |
| 0.2 | Jun 13 2024 | Add power pin VPH 1.2V Reduce PgenIrefOut[11:0] to [1:0] | Tri Vo | Tri Vo |
| 0.3 | Jun 20 2024 | Add VDAC for generating TX Vref Update IDDQ table Add settling time requirement Fixed typo | Tri Vo | Tri Vo |
| 0.4 | Jul 29 2024 | Change Iref_out value from 12.5uA to 25uA Add cell decap for Vreg: dwc_ucie2phy_vreg_decap | Tri Vo | Tri Vo |
| 0.5 | Aug 22 2024 | Change RxVbias_p to RxVbias Change TxVbias_p to TxVbias | Tri Vo | Tri Vo |
| 0.51 | Oct 28 2024 | Add note for the settling time table | Tri Vo | Tri Vo |
| 0.52 | Dec 19 2024 | Add DFT section | Tri Vo | Tri Vo |
| 0.6 | Apr 11 2025 | Change cell name following new conventional name (UCIe-A/S and PHY orientation) | Tri Vo | Tri Vo |
| 0.65 | May 09 2025 | Remove _a/_s in cell name POR: remove pin VCCIO, TxBiasEn, TxCurrAdj[2:0], TxVbias, TxDacSel[7:0], TxVref | Tri Vo | Tri Vo |
| 0.66 | Oct 24 2025 | Update truth table 5-2: PwrOk_VAON = Hi-z when VCCAON = 0 | Tri Vo | Tri Vo |
| 0.67 | Dec 04 2025 | POR: update DFT/Flyover mode condition (user want to enable RX flyover mode) Iref_sel = 0 1 RxBiasEn = 0 1 |  |  |

# Introduction

This Databook describes the information of Power-on reset, Power Clamp and Decap cell for UCIe 2.0 PHY, including design feature, electrical specification, and integration guideline.

# Operating Conditions

## RECOMMENDED OPERATING CONDITIONS

Table 21: Recommended operating conditions for IO

| **Parameter** | **Description** | **Min** | **Typ** | **Max** | **Unit** |
| --- | --- | --- | --- | --- | --- |
| VAA | IO supply voltage for PLL | 1.08 | 1.2 | 1.32 | V |
| VPH | High voltage IO supply | 1.08 | 1.2 | 1.32 | V |
| VCCIO | Driver supply Voltage (normal mode) | 0.45 0.675 | 0.5 0.75 | 0.55 0.825 | V |
| VDD | Core supply Voltage (normal mode) | 0.675 | 0.75 | 0.825 | V |
| VDDREG | Output of voltage regulator | 0.808 | 0.85 | 0.89 | V |
| VCCAON | Always on Auxiliary Supply | 0.675 | 0.75 | 0.825 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | oC |

# dwc_ucie2phy_*clamp

## FEATURES

0.75V I/O supply voltage VCCAON, from -10% to +10%

0.75V Core supply voltage VDD at normal mode, from -7% to +10%

Temperature range -40C to 125C

6A CDM ESD tolerant at ball out bump

EM: 10 years, 105C with self-heating considered, 0.825V power supply

## CELL LIST

Table 31 Power clamp cell list

| **#** | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_vaaclamp_ns | 1.2V power clamp. Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_vaaclamp_ew | 1.2V power clamp. Support UCIe-A/S, EW PHY orientation |
| **3** | dwc_ucie2phy_vddclamp_ns | Core power clamp. Support UCIe-A/S, NS PHY orientation |
| **4** | dwc_ucie2phy_vddclamp_ew | Core power clamp. Support UCIe-A/S, EW PHY orientation |
| **5** | dwc_ucie2phy_pwrclamp_ns | VCCIO/VCCAON power clamp. Support UCIe-A/S, NS PHY orientation |
| **6** | dwc_ucie2phy_pwrclamp_ew | VCCIO/VCCAON power clamp. Support UCIe-A/S, EW PHY orientation |

## PINS DESCRIPTION

Table 32: Pins Description for dwc_ucie2phy_vaaclamp_* cell

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VAA | Power | VAA | Input | IO Power Supply, can use for PLL |
| VSS | Ground | N/A | Input | Ground |

Table 32: Pins Description for dwc_ucie2phy_vddclamp_* cell

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VDD | Power | VDD | Input | Core Power Supply |
| VSS | Ground | N/A | Input | Ground |

Table 34: Pins Description for dwc_ucie2phy_pwrclamp_* cell

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VCCIO2 | Power | VCCIO2 | Input | IO Power Supply, can use for VCCAON/VCCIO |
| VSS | Ground | N/A | Input | Ground |

## FUNCTIONAL BLOCK DIAGRAM

The following block diagram shows the architecture of the clamp cell.

Figure 31 dwc_ucie2phy_vddclamp_* block diagram

Figure 32 dwc_ucie2phy_pwrclamp_* block diagram

Figure 33 dwc_ucie2phy_vaaclamp_* block diagram

## ELECTRICAL PARAMETER

| Parameter | Description | Min | Typ | Max | Units |
| --- | --- | --- | --- | --- | --- |
| Ivccaon | VCCAON average current consumption |  |  | TBU | uA |
| Ivdd | VDD average current consumption |  |  | TBU | uA |

# dwc_ucie2phy_*decap

## FEATURES

This macro provides the decoupling capacitor between power and ground. There are two kinds of decap:

- dwc_uciephy_iodecap_*: supports IO power domain, up to 1.2V
- dwc_uciephy_coredecap_*: support only core power domain
- dwc_ucie2phy_vregdecap_*: unit decap for voltage regulator
## CELL LIST

Table 41 Decap cell list

| **#** | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_iodecap_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_iodecap_ew | Support UCIe-A/S, EW PHY orientation |
| **3** | dwc_ucie2phy_coredecap_ns | Support UCIe-A/S, NS PHY orientation |
| **4** | dwc_ucie2phy_coredecap_ew | Support UCIe-A/S, EW PHY orientation |
| **5** | dwc_ucie2phy_vregdecap_ns | Support UCIe-A/S, NS PHY orientation |
| **6** | dwc_ucie2phy_vregdecap_ew | Support UCIe-A/S, EW PHY orientation |

## PIN DESCRIPTION

Table 42 Pin description of core decap cell

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VDD | Power | VDD | Input | Core Power Supply |
| VSS | Ground | N/A | Input | Ground |

Table 43 Pin description of IO decap cell

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VCCIO2 | Power | VCCIO2 | Input | IO Power Supply, can use for VCCAON/VCCIO |
| VSS | Ground | N/A | Input | Ground |

Table 44 Pin description of Vreg decap

| **Pin** | **Type** | **Level** | **D****irection** | **Description** |
| --- | --- | --- | --- | --- |
| VDDREG | Power | VDDREG | Input | Connect to output of voltage regulator |
| VSS | Ground | N/A | Input | Ground |

## FUNCTIONAL BLOCK DIAGRAM

## ELECTRICAL PARAMETERs

| Parameter | Description | Min | Typ | Max | Units |
| --- | --- | --- | --- | --- | --- |
| Ivccaon | VCCAON average current consumption |  |  | TBU | uA |
| Ivdd | VDD average current consumption |  |  | TBU | uA |

# dwc_ucie2phy_por

## FEATURES

POR macro has 3 main blocks:

- Power sniffer: it senses the VDD level the output PwrOk_VAON signal. When VDD is invalid, PwrOk_VAON goes low, otherwise PwrOk_VAON is high.
- Bias generator: it receives the IREF from bandgap and generate the corresponding Vbias/Iref for TX, RX and 4-phase clock generation. User can adjust the output current by configuring *CurrAdj[*]. User also can select the current source, from bandgap or internal current generation.
- Referent voltage generator: it is 8-bit R-2R based digital to analog converter (DAC) to generate the reference voltage for all TX IOs.
## CELL LIST

Cell list is shown in Table 51. They have the same function and pin interface.

Table 51 POR cell list

| **#** | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_por_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_por_ew | Support UCIe-A/S, EW PHY orientation |

## PIN DESCRIPTION

| **Pin** | **D****irection** | **Type** | **Power domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VCCAON | Input | Power | VCCAON | - | Always ON power supply, it must be available first |
| VPH | Input | Power | VPH | - | 1.2V power supply |
| VDD | Input | Power | VDD | - | Core power supply |
| VSS | Input | Ground | N/A | - | Ground |
| PwrOk_VAON | Output | Digital | VCCAON | - | Indicate the power ok state |
| Iref_bg | Input | Analog | VPH | - | Current reference from bandgap. Typical value is 25uA |
| Iref_sel | Input | Digital | VDD | - | Select current source: 0: Iref_bg 1: Simple internal current generator |
| RxBiasEn | Input | Digital | VDD | - | RX bias enable |
| RxCurrAdj[2:0] | Input | Digital | VDD | - | RX current adjustment |
| RxVbias | Output | Analog | VDD | - | RX Bias voltage output, used to bias NMOS |
| PgenBiasEn | Input | Digital | VDD | - | Phase gen bias enable |
| PgenCurrAdj[2:0] | Input | Digital | VDD | - | Phase gen current adjustment |
| PgenIrefOut[1:0] | Output | Analog | VDD | - | Regulator current reference output. Typical value is 25uA |

## FUNCTIONAL BLOCK DIAGRAM

Figure 51 Block diagram of POR

## OPERATION

Figure 52 Truth table of power sniffer

| **VDD** | **V****CCAON** | **PwrOk_V****AON** |
| --- | --- | --- |
| 0/1 | 0 | Hi-Z |
| 0 | 1 | 0 |
| 1 | 1 | 1 |

| **Rx****CurrAdj[2:0]** | **Current output** |
| --- | --- |
| x00 | 0.75xInom |
| x01 | Normal value (Inom, 100uA) |
| x10 | 1.25xInom |
| x11 | 1.6xInom |

Note: Current output scale factor is not hard constraint as long as it meets the Rx IO requirement.

| **PgenCurrAdj[****2****:0]** | **Current output** |
| --- | --- |
| 000 | 0.8xInom |
| 001 | 0.9xInom |
| 010 | Normal value (Inom, 25uA) |
| 011 | 1.1xInom |
| 100 | 1.2xInom |
| 101 | 1.3xInom |

Note: Current output scale factor is not hard constraint as long as it meets the Phase gen macro requirement.

## INTEGRATION GUIDELINE

- Don’t insert buffer to any output.
- The shielding is required. User must use ground to shield RxVbias. User can use ground or power to shield PgenIrefOut, but ground is more preferred.
- There are 2 reference current outputs that can support up to 2 phase gen. However, user must use one and only one output for one phase gen.
## RTL AND TIMING CONSTRAINTS

### SETTLING TIME

| Parameter | Value | Description |
| --- | --- | --- |
| t_startup_time | 500 ns | The time is measured from power supply crossing 50% of its value to output voltage stabilizing within +/-10% of its stable step value |
| t_bias_settling | 500 ns | After asserting RxBiasEn/PgenBiasEn or any change on TxCurrAdj[*]/RxCurrAdj[*] /PgenCurrAdj[*], user should wait for t_bias_settling, then start any operation modes. |
| t_dac_settling | 500 ns | The time we should wait after increasing/decreasing one DAC code until Vdac output voltage stabilizing within +/-10% of its stable step value |

Note: t_bias_settling is with assumption that Iref_bg has been already settled. If any change of Iref_bg (e.g. system power up, bandgap configuration…), user need to wait for Iref_bg settled then wait for additional t_bias_settling.

### IDDQ MEASUREMENT

Table 52 IDDQ measurement

| Pin | Value | Description |
| --- | --- | --- |
| Iref_sel | 0 | Disable internal bias |
| RxBiasEn | 0 | Disable RX bias |
| PgenBiasEn | 0 | Disable Phase gen bias |

### DFT

| Pin | Value | Description |
| --- | --- | --- |
| Iref_sel | 1 | Enable internal bias |
| RxBiasEn | 1 | Enable RX bias |
| RxCurrAdj | 3’b001 | Default scale factor |
| PgenBiasEn | 0 | Disable Phase gen bias |

### BURN-IN RECOMMENDATION

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run in mission mode.

## IO FLY-OVER MODE CONFIGURATION

Table 53 IO fly-over mode setting

| **Pin** | **Value** | **Description** |
| --- | --- | --- |
| **Iref_sel** | 1 | Enable internal bias |
| **RxBiasEn** | 1 | Enable RX bias |
| **RxCurrAdj** | 3’b001 | Default scale factor |
| **PgenBiasEn** | 0 | Enable Phase gen bias |

## ELECTRICAL PARAMETER

Figure 53 Electrical parameter of POR

| Parameter | Description | Min | Typ | Max | Units |
| --- | --- | --- | --- | --- | --- |
| ps_trip_rise | VDD threshold for pwOK rise | 35 | - | 85 | %VDD |
| ps_trip_fall | VDD threshold for pwOK fall | 15 | - | 75 | %VDD |
| ps_hysteresis | Hysteresis for pwrOK | 50 | - | - | mV |
| Ivccaon | VCCAON average current consumption |  |  | 100 | uA |
| Ivdd | VDD average current consumption |  |  | 50 | uA |
| Iref_in | Input current reference from Bandgap |  | 25 |  | uA |
| Iref_out | Output current |  | 25 |  | uA |

# EMIR CONDITION

Table 69: EMIR simulation condition

| **Parameter** | **EM** | **IR** |  |
| --- | --- | --- | --- |
|  |  | **Dynamic** | **Static** |
| Process | FF | FF | SS |
| Voltage | 0.7875 / 0.525 / 0.803 (VDD/VCCIO/VCCAON) | 0.7875 / 0.525 / 0.803 (VDD/VCCIO/VCCAON) | 0.675 / 0.460 / 0.698 (VDD/VCCIO/VCCAON) |
| Temperature | 105 oC | 105 oC | -40 oC |
| RC extraction | Typical with temperature sensitivity | Typical with temperature sensitivity | Typical with temperature sensitivity |
| Operation mode | Normal operation mode. | Normal operation mode. | Normal operation mode |
| Time step (ratau) | 3 ps | 3 ps | 3 ps |
| Pass condition | <1 (iavg, irms, iswr, iswrl) | <18.75mV for (VDD-VSS) <10mV for (VCCIO-VSS) <22.5mV for (VCCAON-VSS) | <18.75mV for (VDD-VSS) <10mV for (VCCIO-VSS) <22.5mV for (VCCAON-VSS) |

# TESTBENCHES
