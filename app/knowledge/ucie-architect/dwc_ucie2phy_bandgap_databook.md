**UCIe**** ****PHY ****Bandgap**

Databook

e 2.0

Library: dwc_ucie2phy_bandgap

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
| **Dec 29, 2025** | Tri Vo | 0.42 | Change Vbg related power from VPH to VDD () |
| **May 09, 2025** | Tri Vo | 0.41 | Remove _a/s and _ns/ew in cell name () |
| **Apr 11, 202****5** | Tri Vo | 0.4 | Change cell name to follow new conventional name (UCIe-A/S and PHY orientation) Add a note for bg_en and chop_en sequence |
| **Dec 17, 2024** | Tri Vo | 0.36 | Correct DFT setting (bg_en from 0 to 1) |
| **Nov 04, 2024** | Tri Vo | 0.35 | Update DFT recommendation Add Anti-aging recommendation |
| **Oct 28, 2024** | Tri Vo | 0.3 | Add note for IO Fly-over mode configuration |
| **Jun 12, 2024** | Tri Vo | 0.2 | Increase iout_25u to 17 outputs Change pin VDDQ to VPH Add IDDQ/Burn-in test recommendation Add settling time requirement Fix typo |
| **May 07, 2024** | Tri Vo | 0.11 | Update truth table of Vbg selection |
| **Apr 24, 2024** | Cuong Le | 0.1 | Initial version for pin list and functional diagram only |

# Introduction

A robust voltage-reference should be independent in terms of power supply, loading and temperature variations. The Bandgap block aims to generate a voltage-reference that is constant regardless of temperature variations (*temperature independent*).

# Operating Conditions

## RECOMMENDED OPERATING CONDITIONS

Table 21: Recommended operating conditions

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VPH | IO supply Voltage (normal mode) | 1.08 | 1.2 | 1.32 | V |
| VDD | Core supply Voltage (normal mode) | 0.713 | 0.75 | 0.788 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | oC |

Table 22: Support frequencies

| **Function** | **Frequency** |
| --- | --- |
| dwc_ucie2phy_bandgap | - |

Table 23: Timing specification

| **Parameter** | **Min** | **Typ** | **Max** | **Unit** |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

## LIBRARY CHARACTERIZATION CORNERS

Table 24: Corners for library characterization

| Process | Core Voltage (V) | Temperature (C) | RC Corner |
| --- | --- | --- | --- |
| SSG | 0.675 | -40 | typical |
| SSG | 0.675 | 125 | typical |
| FFG | 0.825 | -40 | typical |
| FFG | 0.825 | 125 | typical |
| SSG | 0.675 | 0 | typical |
| FFG | 0.825 | 0 | typical |
| TT | 0.75 | 25 | typical |

# dwc_ucie2phy_bandgap

## FEATURES

- Programmable output referent voltage: from 0.7v to 0.8v.
- 16 outputs of reference current.
- Offset compensation capability.
- Power down mode.
## CELL LIST

Cell list is shown in Table 31. They have the same function and pin interface.

Table 31 Bandgap cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_bandgap | Support both UCIe-A/S, NS/EW PHY orientation |

## PINS DESCRIPTION

Table 32: Pin Description

| **Pin** | **Direction** | **Type** | **Domain** | **Description** |
| --- | --- | --- | --- | --- |
| VPH | Input | Power | VPH | IO supply |
| VDD | Input | Power | VDD | Core supply |
| VSS | Input | Power | VSS | Common ground |
| chop_clk | Input | Digital | VDD | Chopper Clock. The frequence must be in range from 35MHz to 70MHz |
| bg_en | Input | Digital | VDD | Enable bandgap |
| chop_en | Input | Digital | VDD | Enable Chopper Clock 0: disable 1: enable |
| disable_chop_amp | Input | Digital | VDD | Disable Chop Clock for differential pair inputs and outputs 0: enable 1: disable |
| disable_shuffler | Input | Digital | VDD | Disable Chop Clock for current mirrors shuffler 0: enable 1: disable |
| byp_mode | Input | Digital | VDD | Bypass mode enable |
| bgsel[2:0] | Input | Digital | VDD | Select output reference voltage |
| vbg | Output | Analog | VDD | Output reference voltage |
| iout_25u[16:0] | Output | Analog | VPH | Output reference current. Typical value 25uA |

## FUNCTIONAL DESCRIPTION

### Block diagram

Figure 31 Block diagram of dwc_ucie2phy_bandgap

### Operation mode

Table 33 Truth table

| Input | Output | Mode |  |  |
| --- | --- | --- | --- | --- |
| bg_en | **byp_mode** | **vbg** | **iout_25u[*]** |  |
| **0** | x | 0 | High-z | Power down mode, all analog circuit is disabled. |
| **1** | 0 | Bandgap voltage | 25uA | Mission mode |
| **1** | 1 | VDD | 25uA | Bypass mode |

### Vbg selection

Table 34 Vbg selection

| bgsel[2:0] | vbg |
| --- | --- |
| 000 | 0.500v |
| 001 | 0.550v |
| 010 | 0.575v |
| 011 | 0.600v (default code) |
| 100 | 0.625v |
| 1xx | 0. 650v |

Note: the step value may vary depending on technology but the default value is always 0.6v

## ELECTRICAL PARAMETERS

| Specification | Description | Min | Max | Unit | Notes |
| --- | --- | --- | --- | --- | --- |
| Bandgap Voltage | Full-scale output voltage of the bandgap | 720m | 880m | mV | +/- 10 % of nominal 800mV (PVT) |
| Bandgap Voltage Error | Percentage error of nominal voltage | -3 | +3 | % | MC variation |
| Bandgap Tabs Non-linearity | Voltage steps between output tabs | 3.10 | 3.10 | % | increment voltage percentage with each step. |
| Temperature Coefficient | Output voltage change with respect to temperature change | N/A | N/A | uV/C | Looking for best way to implement it |
| Current Consumption | Current drawing from vph supply in normal operation mode | - | 250 | uA | - |
| Current Consumption in PD mode | Current drawing from vph supply in power down mode | - | 15 | uA | - |
| PSRR | Power Supply rejection ratio of the block | - | -10 | dB | Tested frequencies are up to 1GHz |
| Reference Current | External reference current generated using the BG bias voltages | 23.75 | 26.25 | uA | +/- 5 % of nominal 25uA value |
| Startup time | Time for BG to reach 95% of its final voltage |  | 1 | us |  |

## INTEGRATION GUIDELINE

- Don’t insert buffer to vbg and iout_25u[*]. The shielding is required. User can use ground or power to shield but ground is more preferred.
- All DWords can connect to vbg.
- There are 16 reference current outputs that can support up to 16 DWords. However, user uses one and only one output for one DWord.
### DFT

| Pin | Value | Description |
| --- | --- | --- |
| **bg_en** | 1 | Disable bandgap |
| **byp_mode** | 1 | Bypass bandgap voltage, vbg will follow VDD core |

### EMIR CONDITION

Table 35 EMIR condition

| **Parameter** | **EM (*)** | **IR** |  |
| --- | --- | --- | --- |
| Process | FF | FF | SS |
| Voltage supply | Vtyp + 5% | Vtyp + 5% | Vtyp – 10% for VDD Vtyp – 5% for VCCIO |
| Temperature | 105C | 105C | -40C/105C |
| RC extraction | Typical with temperature sensitivity | Typical with temperature sensitivity | Typical with temperature sensitivity |
| Operation mode | Full mode operation, max data rate | Full mode operation, max data rate | Full mode operation, max data rate |
| Time step (ratau) | 3ps | 3ps | 3ps |
| Pass condition | [1 (iavg, irms, acpc) | [15mV for each (VDD-VSS) [8mV for (VCCIO-VSS) [15mV for (VCCAON-VSS) | [15mV for each (VDD-VSS) [8mV for (VCCIO-VSS) [15mV for (VCCAON-VSS) |

### RDIE and CDIE

TBU

### RTL AND TIMING REQUIREMENTS

- When Chopper clock is enabled, user must assert bg_en first, then assert chop_en. Minimum allowed time is 100ns
- Settling time specification:
| Parameter | Value | Description |
| --- | --- | --- |
| t_bias_settling | 20us | Settling time from bandgap enable to vbg valid |
| t_iref_settling | 2us | Settling time from bandgap enable to iout_25u[*] valid |

### IDDQ Measurement

| Pin | Value | Description |
| --- | --- | --- |
| **bg_en** | 0 | Disable bandgap |
| **byp_mode** | 1 | Bypass bandgap voltage, vbg will follow VDD core |

### Burn-in and Anti-aging Recommendation

| Pin | Value | Description |
| --- | --- | --- |
| **bg_en** | 1 | Enable bandgap |
| **byp_mode** | 1 | Bypass bandgap voltage, vbg will follow VDD core |

### IO Fly-over Mode Configuration

For IO Fly-over mode use case, user need to enable bandgap but with byp_mode = 1. User can disable offset compensation feature by disabled chop clock, chop_en = 0, disable_chop_amp = 1 and disable_shuffler = 1.

## TESTBENCHES

| **No** | **Testbench** | **Description ** |
| --- | --- | --- |
| 1 | bandgap_core_tran_(mc)_tb | Basic transient run for bandgap block to test functionality and performance |
| 2 | bandgap_core_tran_alone_(mc)_tb | This version has only the bandgap_core block without bandgap_core_iunit_5u and bandgap_core_bypass. |
| 3 | bandgap_core_dc_(mc)_tb | Provide DC analysis with temperature sweep variation by 15 oC step size form -40 oC to 125 oC to examine voltage-temperature dependency. |
| 4 | bandgap_core_kick_dc_(mc_(tmin|tmax))_tb | Measure the feedback voltage value “kick_ref” that makes the kick-circuit turn off. The TB provides DC analysis that sweeps bandgap output “vrefv<31>” from 0V to 1V by 5mV step increment with respect to temperature variation from -40 oC to 150 oC incremented by 47.5 oC step size. |
| 5 | bandgap_core_dc_op_tb | Provide operating point voltages for all nodes at 0s time. The test-bench aims to find and check MOSFET devices parameters such as id, vgs, vds, vth, vdsat, gm, gds, the intrinsic gain and saturation margin. |
| 6 | bandgap_core_dc_force_(mc)_tb | Forced DC sweep on bandgap loops to ensure the existence of only one valid operating point. |
| 7 | bandgap_core_tran_biascheck_tb | Check and report terminal voltages for all low voltage MOS devices. |
| 9 | bandgap_core_ac_psrr_tb | Provide small signal analysis on Vph supply voltage to measure Power Supply Rejection Ratio ‘PSRR’. |
| 10 | bandgap_core_ac_stab_tb | Provide linear loop stability “lstb” analysis at differential amplifier feedback path to check / measure stability parameter such as phase and gain margins. |
| 11 | bandgap_core_ac_stab_alone_tb | Provide linear loop stability “lstb” analysis at differential amplifier feedback path to check / measure stability parameter such as phase and gain margins without bandgap_core_iunit_5u and bandgap_core_bypass. |
| 12 | bandgap_core_dc_dnl_tb | Provide differential non-linearity test between bandgap tabs. |
| 14 | bandgap_core_tran_emir_tb | EMIR check |
