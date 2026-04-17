**UCIe****2****.0**** ****Local Calibrated Delay Line**** ****(LCDL)**

Databook

UCIe2phy Local Calibrated Delay Line

dwc_ucie2phy_lcdl

dwc_ucie2phy_lcdlsim

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

# Table of Figures

# Revision History

| Rev | Date | Description | Author | Approved by |
| --- | --- | --- | --- | --- |
| 0.10 | Sep 09 2023 | UCIe2.0 LCDL spec initialize | Quang Le | Tri Vo |
| 0.20 | Feb 29 2024 | Update NDL section | Quang Le | Tri Vo |
| 0.3 | April 15 2024 | Add glitchless phase update protocol: +Update lcdl block diagram to support glitchless + Update decoder : coarse decoder & fine decoder to support glitchless +Update ATPG from 9 FF to 19 FF to support glitchless + Update LCDL Pin list: -remove pin dly_sel[8:0] - add new: dly_mux_sel_even[2:0] dly_mux_sel_odd[2:0] dly_sel_crs_even[3:0] dly_sel_crs_odd[3:0] dly_sel_fine[4:0] + Update DFT Scan chain description from 9FF to 19 FF Refer to h120/h130/D900 | Nga Ngo | Tri Vo |
| 0.4 | April 26 2024 | Update pin list Update cal_mode[2] pin Update cal_null pin Update Calibration Block supporting Offset Delay Cancellation in **Figure 1****6** Update Sequence for Offset Delay Cancellation in **Figure ****1****7** Update waveform for 0.5T/1T calibration (**Figure ****1****11**/**Figure 1****12**) and Offset Delay Cancellation Calibration **(****Figure ****1****9**** ****&**** ** **Figure** 110**)** | Quang Le | Tri Vo |
| 0.5 | May 2 2024 | Update Figure 1: add 2pin: cal_mode[2] & cal_null to support with/without offset Calibration | Nga Ngo | Tri Vo |
| 0.6 | May 27 2024 | 1.2.1Update Phase for LCDL. (Update Phase timing constraint : dly_in ↔ dly_update is removed due to LCDL has supported glitch-less when update delay code) | Nga Ngo | Tri Vo |
| 0.7 | Jun 06 2024 | Update Sequence for 0.5T offset cancellation in Figure 18 and config in Table 13 | Quang Le | Tri Vo |
| 0.8 | Sep 27 2024 | Update Table 13 to map with offset calibration sequency in Figure 17 and Figure 18 | Quang Le | Tri Vo |
| 0.9 | Apr 11 2025 | Change cell name to follow new conventional name (UCIe-A/S and PHY orientation) Remove NDL cell | Tri Vo | Tri Vo |
| 0.91 | May 09 2025 | Remove _a/s in cell name | Tri Vo | Tri Vo |
| 1.0 | Jul 14 2025 | Add new macro lcdlsim to support SIM | Tri Vo | Tri Vo |
| 1.05 | Aug 29, 2025 | LCDLSIM: replace pin dly_pin by clk0/90/180/270 | Tri Vo | Tri Vo |
| 1.1 | Oct 02, 2025 | LCDLSIM: add pin force_low to tie dly_out to zero in DFT mode | Tri Vo | Tri Vo |

Reference Documents

# dwc_ucie2phy_lcdl

## Overview

UCIe PHY uses one LCDL (Local Calibrated Delay Line) circuit macro for both mission and track function. In mission, the LCDLs are used to provide the 90 degrees phase shift (0.5UI) between DATA and CLK for the read path so that the CLK is centered into the DATA eye. It is also used to keep track of PVT drifts by continuously measuring the UCIe PHY clock period and instructing control logic for LCDLs to update their values towards the drift.

For the track path, LCDL is used for monitoring the relative variation between the clock and received data. Then the variation is compensated by adjust clock delay from transmitter side.

## Cell list

Cell list is shown in Table 11. They have the same function and pin interface.

Table 11 Cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_lcdl_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_lcdl_ew | Support UCIe-A/S, EW PHY orientation |

## Block Diagram

Figure 11 below shows the architectural block diagram of LCDL.

Figure 11 Block Diagram

## Block Description

The LCDL consists of the following sub blocks:

- **dly_sel**** (phase change) flops** (ATPG):
- The 19 flops on the dly_sel bits in the macro boundary is clocked by the dly_update clock. These flops are added to the scan chain.
- **Input mux**
- The 2x1 input mux allows selection of 2 inputs: calibration clock input (cal_clk) or test clock input (dti), which then goes through the coarse delay and fine delay blocks to the output of the LCDL.
- **Decoder**** **
- The delay setting decoder takes the Phase select signals from the PUB and controls the delay of the coarse delay and fine delay based on the input phase code
- Decode block – coarse even decoder:
Figure 12: LCDL coarse even decoder diagram:

| **sel_e****<2** | **sel_e****<1>** | **sel_e****<0>** | **se<3:0>** | **se<7:4>** | **se<11:8>** | **se<15:12>** | **se<19:16>** | **se<23:20>** | **se<27:24>** | **se<31:28>** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | dly_crseven<3:0> | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 0 | 0 | 1 | 1 | dly_crseven<3:0> | 1 | 1 | 1 | 1 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | dly_crseven<3:0> | 1 | 1 | 1 | 1 | 1 |
| 0 | 1 | 1 | 1 | 1 | 1 | dly_crseven<3:0> | 1 | 1 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 | 1 | 1 | dly_crseven<3:0> | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crseven<3:0> | 1 | 1 |
| 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crseven<3:0> | 1 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crseven<3:0> |

- Decode block – coarse odd decoder:
Figure 13 LCDL coarse odd decoder diagram

| **sel_o****<2>** | **sel_o****<1>** | **sel_o****<0>** | **so<3:0>** | **so<7:4>** | **so<11:8>** | **so<15:12>** | **so<19:16>** | **so<23:20>** | **so<27:24>** | **so<31:28>** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | dly_crsodd<3:0> | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 0 | 0 | 1 | 1 | dly_crsodd<3:0> | 1 | 1 | 1 | 1 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | dly_crsodd<3:0> | 1 | 1 | 1 | 1 | 1 |
| 0 | 1 | 1 | 1 | 1 | 1 | dly_crsodd<3:0> | 1 | 1 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 | 1 | 1 | dly_crsodd<3:0> | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crsodd<3:0> | 1 | 1 |
| 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crsodd<3:0> | 1 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | dly_crsodd<3:0> |

- Decode block – fine decoder:
Table 12 LCDL coarse odd decoder diagram

- **Co****re**** ****delay ****block**
- The core delay block comprises of the coarse delay block and fine delay block.
**Figure ****1****4****: ****Coarse Delay and Fine Delay Block Diagram**:

- **Corase**** delay block**
- Coarse delay block are selected using input dly_sel_crs_even[3:0], dly_sel_crs_odd[3:0] and the range extension select bits dly_mux_sel_even[2:0], dly_mux_sel_odd[2:0] to give a desirable delay
- The coarse delay chain provides two output clock signals **out_a**** & ****out_b** which goes to the fine delay block
- Each coarse block produces a certain amount of delay, it depends on the total steps of the fine delay block and the desired average step size. For example, if the fine delay block has 16 steps and the average step size is 1ps in FF corner, the ideal delay of each coarse block should be 16x1ps = 16ps.
- A coarse block consists of a forward path mux and even/odd backward path muxes as shown in **Figure ****1****4** above.
- The decoding scheme for the coarse delay chain is ‘0’ hot. The forward path phase input will wrap around to the backward when select=0. When select=1, the forward path propagates the phase clock to the next mux in the forward path and the backward mux selects the input coming from the previous backward mux in the coarse delay chain.
- dly_mux_sel_even[2:0] and dly_mux_sel_odd[2:0] inputs are used for coarse mux row selection for the LCDL to extend range. Below are the selection setting:
- 000 = coarse mux 0-7
- 001 = coarse mux 8-15
- 010 = coarse mux 16-23
- 011 = coarse mux 24-31
- 100 = coarse mux 32-39
- 101 = coarse mux 40-47
- 110 = coarse mux 48-55
- 111 = coarse mux 56-63
- **Fine delay block**
- The fine delay block is used to provide 16 fine delay steps. These 16 steps are selected by using delay setting input dly_sel_fine[4:0] and are thermometric encoded inside the LCDL
- The phase signals out_a and out_b from the coarse delay block propagate to the interpolated to generate the 1-LSB resolution of delay
Figure 15 LCDL interpolating inverters 16 steps

- **Calibration block**
- In calibration mode, the LCDL is used to detect one cycle (1T) or a half cycle (0.5T) phase shift of input clock signal ‘cal_clk’ via ‘cal_mode[1]’ port configuration. The half cycle (0.5T) calibration is only used in low frequency mode with the input clock frequency equal or less than 2Ghz. LCDL is also used to keep track of PVT drifts by continuously measuring the Pclk clock period and updating the LCDLs towards this drift.
- Calibration block takes delayed and null delayed outputs out of the delay line after the coarse and fine delay blocks and passes them through flops and a phase detector to calibrate/measure 1T/0.5T input clock(cal_clk) delayed phase shift of the delay line.
- In order to provide non-delayed or null-delay outputs from the delay line for calibration, a set of identical fine and coarse blocks with delay settings of “0” is used. This path will only have the insertion delay.
- The flip-flops used in the calibration block are resettable and the asynchronous cal_reset pin will reset the calibration logic at the beginning of calibration mode. The cal_reset is active high.
- Due to the imbalance inside the LCDL because of different parasitic of routing nets, and the setup/hold requirements of these FFlop’s, the setting of input dly_sel* resulting in a rise of output cal_out does not imply an exact delay of 1T/0.5T between ndly_clk and dly_clk. Such a difference in delay is an offset and that offset will impact the accuracy of 1T/0.5T delayed phase shift value.
- Offset cancellation feature has been implemented to eliminate the calibration offset error in MC variation to reduce the strobe alignment error.
- The calibration cycle for 0.5T and 1T is shown in
- **Figure**** ****1****11** and **Figure ****1****12** respectively.
**Figure ****1****6****: ****Calibration block diagram**

Table 13: Calibration mode configuration for offset cancellation

| **Mode** | **cal_mode****[1]** | **cal_mode****[****2****]** | **cal_null** |
| --- | --- | --- | --- |
| Offset cancel ON. Null offset delay calibration mode | 1’b0 | 1’b1 | 1’b1 |
| Offset cancel ON. 1T delay calibration mode | 1’b0 | 1’b0 | 1’b1 |
| Offset cancel ON. 0.5T delay calibration mode | 1’b1 | 1’b0 | 1’b1 |
| Offset cancel OFF | 1’bx | 1’b0 | 1’b0 |

Figure 17 : Offset Cancellation Sequence Diagram for 1T

Figure 18 : Offset Cancellation Sequence Diagram for 0.5T

Figure 19 : Offset Null Delay Calibration (cal_mode[2] = 1, cal_null = 1)

Figure 110 : Offset 1T Delay Calibration (cal_mode[2] = 0, cal_null = 1)

Table 14: Calibration mode configuration constraint by input clock frequency.

| **Mode** | **c****al_mode****[1]** | **cal_clk**** frequency** |
| --- | --- | --- |
| 1T(one cycle) calibration | 1’b0 | 4Ghz-8Ghz |
| 0.5T(half cycle) calibration | 1’b1 | 2Ghz |

**Figure ****1****11****: ****0.5****T**** ****C****alibration**** (****cal_****mode****[1]****=1)**** ****Cycle**** for ****cal_clk****=2G****H****z**

Figure 112: 1T Calibration (cal_mode[1]=0) Cycle for cal_clk=8GHz(or 4GHz)

- **Bypass mux**
The bypass mux serves two purposes -

- The primary input, byp_in is used for scan/DFT purposes and muxes in atpg clock/test clock when LCDL is in bypass mode.
- Bypass mode is also used to gate the mission mode output, dly_out, during calibration and test mode.
## Features

- Power supply at IP port:
- Normal voltage range: 0.75v +10%/-10%.
- Junction operation temperature:
- Performance range: -40oC to 125oC.
- EM: 10 years, 105oC with self-heating considered, 0.75V + 10% power supply.
- Clock frequency support: 2GHz - 8GHz.
- Master and Slave Delay Line structure to support VT compensation tracking mode.
- Precise adjustment step: Less than 2ps (32 steps in 1UI).
- Support test mode: Linearity test, Ring oscillator test.
- Built-in scan chain for the control logic.
- Burn-in mode.
- Provide 1007 delay step settings via 19bit input port configuration.
- Glitchless arbitrary phase change if no edge is propagating through the LCDL, as long as input is parked consistent with park_even/park_odd inputs. Bypass mux is not needed to avoid glitches propagating to the output of LCDL. This avoids the race with bypass signal in Implementation land.
- For glitchless update, park_even and park_odd work differentially so ideally only one input signal could have been used for this functionality. However, parking the alternate muxes differentially doesn’t yield best results for aging, so if aging becomes a concern either for this technology or future ports we have the flexibility to improve aging by parking both signals to be of the same polarity but at the cost of glitching the LCDL. *Table **1**5* shows the settings for ‘park_even’ and ‘park_odd’ that follow the input clock deactived/idle state. As shown in the table, the ‘park_even’ have to be set same state as the deactived/idle state of input clocks of LCDL to avoid glitching. The ‘park_odd’ is inverted state of ‘park_even’.
Table 15 Park pins settings for LCDL.

| **Input****(****dly****_in****/****dti****/****cal_clk****) ****de****-****active****/idle**** ****state** | **park_even** | **park_odd** |
| --- | --- | --- |
| 0 | 0 | 1 |
| 1 | 1 | 0 |

- LCDL expects the gated cal_clk at its input during calibration mode (no deglitch circuitry is present within LCDL to gate cal_clk).
- Second edge detection for the calibration Phase Detector to avoid picking up extra jitter on the first edge.
### Glitchless phase update protocol

When clock edge propagating through the LCDL, we can only change the phase by 1LSB. Need to apply a sequencer to make sure that the code update in LCDL are done respecting the “glitchless” protocol. In particular, the phase shall be updated one lcdl native LSB at this time.

Before a change on *dly_mux_sel* or dly_sel_crs*, dly_sel_fine* has to be unchanged to avoid glitches for the CK case. It means that,

- In the **increment** sequence, “dly_sel_fine*” will be update first and followed by “dly_mux_sel*” and “dly_sel_crs*” update.
- In the **decrement** sequence, “dly_mux_sel*” and “dly_sel_crs*” will be updated first and followed by “dly_sel_fine*” update
Figure 113 Glitchless phase update : MUXSEL & CRSSEL EVEN CODE CHANGE

Figure 114 **Glitchless phase update : CRSSEL EVEN CODE CHANGE & MUXSEL static**** **

Figure 115 **Glitchless phase update : MUXSEL & CRSSEL ODD CODE CHANGE**** **

Figure 116 **Glitchless phase update : CRSSEL ODD CODE CHANGE & MUXSEL static**** **

## Pin List

Table 16 LCDL Pin list

| **Pin Name** | **Direction** | **Power Domain** | **Clock Domain** | **Freq****uency** | **Function** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | VDD | Async | - | Power Supply |
| VSS | Input | 0 | Async | - | Ground |
| dly_in | Input | VDD | Self | 8 GHz | Delay Line Input: Input signal to be delayed. |
| dly_update | Input | VDD | Self | 2 GHz | Clock for the delay line delay select (dly_sel) flops |
| park_even | Input | VDD | - | - | Input that controls parking direction for glitch-less phase update, works differentially with park_odd. |
| park_odd | Input | VDD | - | - | Input that controls parking direction for glitch-less phase update, works differentially with park_even. |
| dly_out | Output | VDD | dly_in/ byp_in | 8 GHz | Delay Line Output: Output delayed by the delay selected by dly_sel. Refer to truth table Table 17. |
| cal_mode[2:0] | Input | VDD | Async | - | **cal_mode****[0]** is used to set the LCDL into Calibration mode that follow the Functional Modes table-Table 17. In this mode the delay line calibrates to 1T/0.5T over VT drifts. **c****al_mode****[1]**** **is used to select mode for calibration. 0: calibrate 1T (full cal_clk cycle). 1: calibrate 0.5T (half cal_clk cycle) that only used in low frequency mode cal_clk freq <= 2Ghz). **cal_mode****[2]**** **is used to select mode for calibration offset cancellation feature. 1 : config for calibration block to calibrate for offset delay 0 : config for calibration block to calibrate for 1T delay |
| cal_clk | Input | VDD | Self | 8 GHz | Calibration Clock: Clock passed through the delay line for 1T/0.5T measurement is in calibration mode. This clock is used to sample the calibration measure mode enable input, cal_en. |
| cal_en | Input | VDD | Async | - | Calibration Enable: Enables measurement phase for calibration. This signal is sampled by the calibration clock . |
| cal_reset | Input | VDD | Async | - | Asynchronous reset pin to reset the calibration logic |
| cal_null | Input | VDD | Async | - | Selection pin to config null delay for offset cancellation mode 1 : Enable null delay for cancellation mode, extend delay of null delay to the amount of 16 delay step. 0 : Config 0T delay for null delay, back to original scheme as gen 1 |
| cal_out | Output | VDD | - | - | Calibration Output: Indicates the status of the delayed clock relative to the reference (null delay) clock. cal_out = 1 for delay > 1T/0.5T cal_out = 0 for delay < 1T/0.5T cal_out gets sampled by a flop clocked by lclk clock outside LCDL. |
| test_mode | Input | VDD | Async | - | Test Mode: Selects the test modes of the delay line. 0 = Mission mode or calibration mode 1 = Test mode |
| dti | Input | VDD | - | 8 GHz | Test Input: Delay line input during test mode |
| dto | Output | VDD | dti | 8 GHz | Test Output: Delay line output during test mode |
| byp_in | Input | VDD | - | 8 GHz | Bypass mux input for bypass mode |
| byp_mode | Input | VDD | - | - | Bypass mode enable. When asserted, the input byp_in is chosen to be output at dly_out |
| atpg_mode | Input | VDD | - | - | Scan mode: when asserted, the dly_sel flops are in scan mode |
| atpg_se | Input | VDD | - | - | dly_sel flops scan chain enable |
| atpg_si | Input | VDD | - | - | dly_sel flops scan chain input |
| atpg_so | Output | VDD | - | - | dly_sel flops scan chain output |
| force_max_delay | Input | VDD | Async | - | Force dly_sel bits to high for burn-in |
| dly_mux_sel_even[2:0] | Input | VDD | dly_update |  | 000 = even coarse mux 0-7 001 = even coarse mux 8-15 010 = even coarse mux 16-23 011 = even coarse mux 24-31 100 = even coarse mux 32-39 101 = even coarse mux 40-47 110 = even coarse mux 48-55 111 = even coarse mux 56-63 |
| dly_mux_sel_odd[2:0] | Input | VDD | dly_update |  | 000 = odd coarse mux 0-7 001 = odd coarse mux 8-15 010 = odd coarse mux 16-23 011 = odd coarse mux 24-31 100 = odd coarse mux 32-39 101 = odd coarse mux 40-47 110 = odd coarse mux 48-55 111 = odd coarse mux 56-63 |
| dly_sel_crs_even[3:0] | Input | VDD | dly_update |  | Delay line select for the even coarse delay backward muxes |
| dly_sel_crs_odd[3:0] | Input | VDD | dly_update |  | Delay line select for the odd coarse delay backward muxes |
| dly_sel_fine[4:0] | Input | VDD | dly_update |  | Delay line select for the fine delay 16 bits interpolator |

## LCDL Functional Modes and Truth Table

The LCDL has 3 functional modes: mission mode, calibration mode and test mode. In all the 3 functional modes, the LCDL delays the input signal by a delay amount depending on the setting of delay select input (dly_sel_crs_*[3:0], dly_mux_sel_*[2:0], dly_sel_fine[3:0]). The functional modes scheme is implemented as shown in *Figure **1**17*.

Figure 117: Functional Modes diagram.

### Mission mode

Mission mode is the normal operating mode in which input signal dly_in is delayed and passed to LCDL outputs. The amount of delay is determined by the delay setting inputs. LCDL input dly_in connects to different signals based on its usage in mission mode.

### Calibration mode

Calibration mode is used to determine delay setting required to delay the input signal by a desirable delay time (1T/0.5T). In this mode, the delay line calibrates to 1T/0.5T over VT drifts. The mission mode output dly_out is gated to *byp_in* in calibration mode.

### Test mode

Test mode is used for test purpose – linearity testing and ring oscillator mode. The mission mode output dly_out is gated to *byp_in* in test mode.

### Bypass mode

In any mode, the LCDL can be placed in bypass or non-bypass mode. Bypass mode can be used for passing scan clock input byp_in to the dly_out output of the LCDL. This mode is also used for gating the dly_out when LCDL is in calibration mode and test mode. Calibration does not need additional gater at the output of the LCDL which helps with jitter and implementation timing.

### Burn-in mode

The LCDLs need to be forced into ring oscillator mode with maximum delay code for burn-in. To support this, test_mode = 1 and force_max_delay is set to 1 to force maximum delay code on all the phase inputs asynchronously (dly_sel_crs_*[3:0], dly_mux_sel_*[2:0], dly_sel_fine[4:0]).

#### Functional Modes Truth Table

Table 17 LCDL Funtional Modes Truth Table

| **MODE** | **byp_mode** | **test_mode** | **cal_mode****[0]** | **force_max_delay** | **Input selection**** for the delay chain** | **dly_****out**** source** | **d****to**** source** | **Note** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mission | 0 | 0 | 0 | 0 | dly_in | dly_in | 0 |  |
| Calibration | 1 | 0 | 1 | 0 | cal_clk | byp_in | 0 | Force byp_in=0 |
| Test/Ring oscillator | 0/1 | 1 | x | 0 | dti | dti/byp_in | dti |  |
| Burn-in | 0/1 | 1 | x | 1 | dti | dti/byp_in | dti |  |
| Bypass | 1 | 0/1 | 0 | 0 | dti/dly_in | byp_in | 0/dti |  |

## DFT mode.

### DFT Scan chain description.

LCDL support one scan chain including 19-D-flipflops for delay setting. There is one input clock ‘*dly_update**’* which used for DFT scan test.

Table 18: DFT scan chain information

| **Scan chain No.** | **DFT ****input ****Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | dly_update | atpg_si | atpg_se | atpg_so | rising | 19 | LCDL scan chain |

Figure 118: DFT scan chain implementation.

### DFT integration.

Before DFT scan chain test, the bypass mode should be asserted to avoid glitched at output dly_out. Follow the *Table **1**9* and *Table **1**10* for the inputs control.

Table 19: Configuration for Bypass mode before start DFT mode.

| **MODE** | **byp_mode** | **test_mode** | **cal_mode****[0]** | **force_max_delay** | **Input selection** | **dly_****out**** source** | **dto**** source** | **Note** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DFT MODE | 1 | X | 0 | 0 | X | byp_in | X | Force byp_in=0, atpg_mode=1 |

Table 110: Control inputs in DFT mode.

| **Scan Test Phase** | **Input name** | **Bus width** | **Value** |
| --- | --- | --- | --- |
| ASST Scan Shift | atpg_mode | 1 | 1’b1 |
|  | atpg_se | 1 | 1’b1 |
| ASST Scan Capture | atpg_mode | 1 | 1’b1 |
|  | atpg_se | 1 | 1’b0 |
| Stuck-At Scan Shift | atpg_mode | 1 | 1’b1 |
|  | atpg_se | 1 | 1’b1 |
| Stuck-At Scan Capture | atpg_mode | 1 | 1’b1 |
|  | atpg_se | 1 | 1’b0 |

Figure 119 Scan Test Control

## RTL Assertions and Constraints.

### Update Phase for LCDL.

In the delay phase setting update sequence, the input clock of LCDL must be de-active to avoid glitched happen at output. There are the timing constraints for input “*dly_update**”* and input clocks “*dti**/**cal_clk*” setting.

Figure 120 Update Phase timing constraint waveforms

**Note 1. **The last falling edge of “*dti**/**cal_clk*” has to pass through the LCDL before updating phase. We have 4T(4 Pclk cycles) from the last falling edge of “*dti**/**cal_clk*” to rising edge of “*dly_update**”*.** **This has to account for the worst case 2.5T delay phase setting, so the insertion delay must be less than 1.5T.

**Note 2. **We have 3T( 3Pclk cycles) from the rising edge of “*dly_update**”* to the first valid edge of “*dly_in**/**dti**/**cal_clk*”. The circuit takes 3T for the decoder delay.

Table 111: Summary timing constraints for update phase setting.

| Requirement | Min (ps) | Note |
| --- | --- | --- |
| Falling dly_in ↔ Rising dly_update | 500 | 4Pclk |
| Falling dti ↔ Rising dly_update | 500 | 4Pclk |
| Falling cal_clk ↔ Rising dly_update | 500 | 4Pclk |
| Rising dly_update ↔ Rising dly_in | 500 | 4Pclk |
| Rising dly_update ↔ Rising dti | 500 | 4Pclk |
| Rising dly_update ↔ Rising cal_clk | 500 | 4Pclk |

Note: dly_in <-> dly_update is removed due to LCDL has supported glitch-less when update delay code

### Switch Operation mode.

In the operation mode switching sequence, all input clocks of LCDL, “*dly_in**/**dti**/**cal_clk**/**byp_in*” must be set de-active/idle to avoid glitched happen at output. There are the timing constraint for operation mode switching setting.

Figure 121 Switch operation mode timing constraint waveforms

**Note****1****: **There is the 4T(4Pclk cycles) worst case of 2.5T delay phase setting and 1.5T insertion delay. The input clock have to completely pass through the delay chain before start switching mode.

**Note2:** we have to wait 2T(2 Pclk cycles) or 0.5lclk for operation mode control signal stable before start toggle the clock.

Table 112: Summary timming constraints for operation mode switching

| Timing Relation | Min (ps) | Note |
| --- | --- | --- |
| Falling dly_in ↔ test_mode toggling | 500 | Removed by jira |
| Falling cal_clk ↔ test_mode toggling | 500 |  |
| Falling byp_in ↔ test_mode toggling | 500 |  |
| Falling dti ↔ test_mode toggling | 500 | 4Pclk |
| Falling dly_in ↔ cal_mode[0] toggling | 500 | 4Pclk |
| Falling byp_in ↔ cal_mode[0] toggling | 500 | 4Pclk |
| Falling dti ↔ cal_mode[0] toggling | 500 | Covered by internal logic |
| Falling cal_clk ↔ cal_mode[0] toggling | 500 | Covered by calibration sequence |
| Falling dly_in ↔ byp_mode toggling | 500 | 4Pclk |
| Falling cal_clk ↔ byp_mode toggling | 500 | Covered by calibration sequence |
| Falling dti ↔ byp_mode toggling | 500 | Removed by jira |
| Falling byp_in ↔ byp_mode toggling | 500 | 4Pclk |
| Rising test_mode ↔ Rising dti | 500 | 4Pclk |
| Rising cal_mode[0] ↔ Rising cal_clk | 500 | 4Pclk |
| Rising byp_mode ↔ Rising byp_in | 500 | 4Pclk |
| Rising (~test_mode&~cal_mode[0] &~byp_mode) mission mode ↔ Rising dly_in | 500 | 4Pclk |

## Interface Requirements.

### Timing Requirements.

Table 113: Interface Timing requirements

| **Pin Name** | **Pin Direction** | **Type** | **Max** **Frequency (GHz)** | **Max** **Slew (ps)** | **Max** **Cap** **(****fF****)** | **Min** **Pulse-width** **(ps)** | **SDF condition** | **Note** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dly_sel[8:0] | Input | Data | 1 | 60 | - | - |  |  |
| dly_update | Input | Clock | 2 | 50 | - | 50 |  |  |
| park_even | Input | Enable | - | 60 | - | - |  |  |
| park_odd | Input | Enable | - | 60 | - | - |  |  |
| dly_in | Input | Data | 8 | 16 | - | 47.5 |  |  |
| dly_out | Output | Data | 8 | 16 | 20 | - |  |  |
| cal_mode[1:0] | Input | Enable | - | 60 | - | - |  |  |
| cal_clk | Input | Clock | 8 | 16 |  | 44 | !cal_mode[1] | For High frequencies |
| cal_clk | Input | Clock | 2 | 16 | - | 215 | cal_mode[1] | For Low frequency |
| cal_en | Input | Enable | - | 60 | - | - |  |  |
| cal_reset | Input | Reset | - | 60 | - | - |  |  |
| cal_out | Output | Data | - | 20 | 15 | - |  |  |
| test_mode | Input | Enable | - | 60 | - | - |  |  |
| dti | Input | Data | 8 | 16 | - | 60 |  |  |
| dto | Output | Data | - | 16 | 15 | - |  |  |
| byp_in | Input | Data | 8 | 16 | - | 50 |  |  |
| byp_mode | Input | Enable | - | 60 | - | - |  |  |
| atpg_mode | Input | Enable | - | 60 | - | - |  |  |
| atpg_se | Input | Enable | - | 60 | - | - |  |  |
| atpg_si | Input | Data | 2 | 30 | - | - |  |  |
| atpg_so | Output | Data | 2 | 30 | 15 | - |  |  |
| force_max_delay | Input | Enable | - | 60 | - | - |  |  |
| VDD | Input | Power | - | - | - | - |  |  |
| VSS | Input | Ground | - | - | - | - |  |  |

Note: Slew value is 20%-80%

## Command Specific Registers (NONE)

Table 114 LCDL CSR defaults

| **CSR Name** | **Function** | **Default Value** |
| --- | --- | --- |
|  |  |  |

## Timing Parameters.

### Delay Parameters.

Table 115: Delay parameters

| **Parameter** | **Description** | **Min** | **Nom** | **Max** | **Units** |
| --- | --- | --- | --- | --- | --- |
| t_stepsize | Average delay step size | 0.6 | 1.2 | 2 | ps |
| t_zerodly | Insertion(zero-tap) delay (from dly_in to dly_out) | 55 | 110 | 187 | ps |
| t_roscdly | Ring oscillator (zero-tap) delay(from dti to dto) | 65 | 120 | 200 | ps |
| t_caldly | Calibration (zero-tap) delay (from cal_clk to dly_cal_out) | 65 | 120 | 200 | ps |
| t_bypdly | Bypass delay (from byp_in to dly_out) | 25 | 40 | 70 | ps |

### VT Drift Scaling Factors.

Table 116: t_stepsize scaling factor by VT drift at Slow (Max step delay) process.

| **VT** | **-40** | **25** | **125** |
| --- | --- | --- | --- |
| **Vmin** | **1** | 0.84 | 0.77 |
| **Vnom** | 0.65 | 0.64 | 0.63 |
| **Vmax** | 0.53 | 0.6 | 0.6 |

Table 117: t_stepsize scaling factor by VT drift at Typical (Nominal step delay) process.

| **VT** | **-40** | **25** | **125** |
| --- | --- | --- | --- |
| **Vmin** | 1.35 | 1.31 | 1.26 |
| **Vnom** | 1 | **1** | 1.12 |
| **Vmax** | 0.76 | 0.76 | 0.82 |

Table 118: t_stepsize scaling factor by VT drift at Fast (Min step delay) process.

| **VT** | **-40** | **25** | **125** |
| --- | --- | --- | --- |
| **Vmin** | 1.45 | 1.42 | 1.41 |
| **Vnom** | 1.23 | 1.24 | 1.27 |
| **Vmax** | **1** | 1.15 | 1.2 |

## Simulation Plan

### List of Testbenches

| **TestBench** | **Description** | **Spec Parameter extracted** |
| --- | --- | --- |
| lcdl_top_mission_<PVT>.bbSim lcdl_top_mission_dcin_<min/max>_<PVT>.bbSim | LCDL is in mission mode with an input pulse at dly_in.Separate TB for each PVT with multiple corners to sweep delay setting. lcdl_top_mission_<PVT>.bbSim (50% input duty cycle) lcdl_top_mission_dcin_<min/max>_<PVT>.bbSim (worst input duty cycle - min/max pulse high) | 1. Insertion Delay |
|  |  | 2. Delay Step |
|  |  | 3. Max Step |
|  |  | 4. LSB (avg step size) |
|  |  | 5. INL |
|  |  | 6. DNL |
|  |  | 7. 1st/2nd edge offset |
|  |  | 8. DCD |
|  |  | 9. Lock code, 1T(8GHz) code, 0.5T(2GHz) code |
|  |  | 10. Output slew |
| lcdl_top_mission_mc_<PVT>.bbSim lcdl_top_mission_mc_dcin_<min/max>_<PVT>.bbSim | LCDL in mission mode with an input pattern on dly_in. delay settings are updated with a vector file. Separate TB for each PVT with 330 monte trials for 3sigma MC-Sigamp simulation. lcdl_top_mission_mc_<PVT>.bbSim (50% input duty cycle) lcdl_top_mission_mc_dcin_<min/max>_<PVT>.bbSim (worst input duty cycle - min/max pulse high) | 1. MC LSB(avg step size) |
|  |  | 2. MC DNL (max) |
|  |  | 3. MC INL (max) |
|  |  | 4. MC INL at lock_code +/-4 |
|  |  | 5. MC t_insertion |
|  |  | 6. MC max step |
|  |  | 7. MC 1st edge 2nd edge offset |
| lcdl_top_minfreq.bbSim | TB to check delay and functionality at max tap setting. And then calculate the Frequency values | 1. LCDL total delay(min) @tap511 |
|  |  | 2. LCDL locking frequency (min) |
|  |  | 3. LCDL 1T calibration frequency (min) |
|  |  | 4. LCDL 0.5T calibration frequency (min) |
| lcdl_top_crs_dec_delay.bbSim lcdl_top_fine_dec_delay.bbSim | crs_delay TB switches tap setting from 0 to all coarse jumps and measure decoder delay for each case.‘fine_dec' switches tap setting from all fine jumps to the worst case from above TB. Both TBs are run for the slowest corner only. | 1. Coarse decoder delay (max) |
|  |  | 2. Fine decoder delay (max) |
| lcdl_top_mission_dcd.bbSim | Measure duty cycle distortion in mission mode from dly_in to dly_out from code 0x20(32) to lock_code +8 setting with worst input duty cycle(min/max pulse high). | 1. DCD at for mission mode 8Ghz |
| lcdl_top_mission_0T_dcd_dcin_<min/max>_mc_<PVT>.bbSim | (For data path) Measure duty cycle distortion in mission mode from dly_in to dly_out from 0T to code 8 setting with worst input duty cycle(min/max pulse high). Separate TB for each PVT with 330 monte trials for 3sigma MC-Sigamp simulation. | MC DCD at code 0 to code 8 |
| lcdl_top_mission_dcd_dcin_<min/max>_mc_<PVT>.bbSim | (For clock path) Measure duty cycle distortion in mission mode from dly_in to dly_out from code 0x20(32) to lock_code +8 setting with worst input duty cycle(min/max pulse high). Separate TB for each PVT with 330 monte trials for 3sigma MC-Sigamp simulation. | MC DCD at code 0x20(32) to lock_code +8 |
| lcdl_cal_sr_offset.bbSim | Measure the offset between dly_clk path and ndly_clk path of cal_sr block only. | 1. tcal_sr_offset |
| lcdl_top_cal_offset_0p5T_mc_<PVT>.bbSimlcdl_top_cal_offset_1T_mc_<PVT>.bbSim | LCDL in calibration mode with pulse input on cal_clk. Calibration Offset measurement at tap 0.5T/1T for 2GHz/8GHz. Separate TB for each PVT with 330 monte trials for 3sigma MC-Sigamp simulation. | 1. MC 1T Calibration offset |
|  |  | 2. MC 0.5T Calibration offset |
| lcdl_top_cal_dcd.bbSim | Measure duty cycle distortion in calibration mode from cal_clk to dly_cal_out at code 1T/0.5T(8GHz/2GHz) +/-8 setting with worst input duty cycle(min/max pulse high). | 1. DCD in calibration mode |
| lcdl_PD_offset.bbSim | Phase detector resolution time and offset time MC sigamp | 1. Phase Detector resolution time 2. Phase Detector offset time |
| lcdl_PD_offset_mc.bbSim | Phase detector resolution time and offset time with MC sigamp | 1 MC Phase Detector’s resolution time 2. MC Phase Detector’s offset time |
| lcdl_top_glitch_check.bbSim | Check glitching at output clock(dly_out, dto) when updating dly_sel and switching functional mode. | Check for glitch |
| lcdl_top_emir_she_<mode>.bbSim | LCDL is put into all modes (active/atpg/cal_0p5t/cal_1t/bypass/test_burnin) of operation at fastest operating corner for EMIR check with SHE flow. | EM and IR drop |
| lcdl_top_power.bbSim | LCDL is in mission mode with lock_code setting and toggle input clock to measure the active current. | 1. Active current |
| lcdl_top_leakage.bbSim | LCDL is in mission mode with lock_code setting and idle/de-active input clock to measure the leakage current. | 1.Leakage current |
| lcdl_top_dly_supply_sensitivity.bbSim | TB to check power supply sensitive of delay | 1. Delay’s Power Supply sensitive |
| lcdl_top_dly_temp_drift.bbSim | TB to check the delay variation due to temperature drift | 1. Delay’s Temp drift |
| lcdl_top_aging_periodic_mission.bbSim | LCDL stress in mission and measure in mission. TB to check effect of aging on delay and DCD under different stress conditions. The input clock frequency is max(8GHz). | 1. DCD due to aging |
|  |  | 2. Rise/Fall delays |
| lcdl_top_aging_low_freq_periodic_mission.bbSim | LCDL stress in mission and measure in mission. TB to check effect of aging on delay and DCD under different stress conditions. The input clock frequency is anti-aging frequency(25Mhz GHz). | 1. DCD due to aging |
|  |  | 2. Rise/Fall delays |
| lcdl_top_aging_periodic_cal.bbSim | LCDL stress in mission and measure in calibration mode. TB to check effect of aging on Tcal_offset under different stress conditions. The input clock frequency is max(8GHz). | 1. Tcal_offset at 1T (8GHz) 2. Tcal_offset at 0.5T (2GHz) |
| lcdl_top_aging_low_freq_periodic_cal.bbSim | LCDL stress in mission and measure in calibration mode. TB to check effect of aging on Tcal_offset under different stress conditions. The input clock frequency is anti-aging frequency(25Mhz GHz). | 1. Tcal_offset at 1T (8GHz) 2. Tcal_offset at 0.5T (2GHz) |
| lcdl_top_dcck.bbSim | For dynamic CCK check. |  |
| lcdl_min_pulse_width_dly_update/dti/cal_clk.bbSim | [For Timing measurement] Measure min pulse width of input pin dly_update/dti/cal_clk. |  |
| lcdl_min_pulse_width_<dly_update/dti/cal_clk>_mc.bbSim | [For Timing measurement] Measure min pulse width with MC of input pin dly_update/dti/cal_clk |  |
| lcdl_top_dly_update_atpg_so_aging.bbSim | [For Timing measurement] TB to check effect of aging on arc delay from dly_update to atpg_so |  |
| lcdl_top_<tsu/thd>_atpg_dly_update_aging.bbSim | [For Timing measurement] TB to check effect of aging on arc setup time and hold time from atpg_so/atpg_se/atpg_mode to dly_update |  |
| lcdl_top_<tsu/thd>_dly_sel_dly_update_aging.bbSim | [For Timing measurement] TB to check effect of aging on arc setup time and hold time from dly_sel<8:0> to dly_update |  |
| lcdl_top_timi_arc_aging.bbSim | [For Timing measurement] TB to check effect of aging on timing arcs: dly_in àdly_out dti àdto cal_clk àcal_out |  |
| lcdl_top_dly_update_atpg_so_ir_drop.bbSim | [For Timing measurement] TB to check effect of IR drop on arc delay from dly_update to atpg_so |  |
| lcdl_top_<tsu/thd>_atpg_dly_update_ir_drop.bbSim | [For Timing measurement] TB to check effect of IR drop on arc setup time and hold time from atpg_so/atpg_se/atpg_mode to dly_update |  |
| lcdl_top_<tsu/thd>_dly_sel_dly_update_ir_drop.bbSim | [For Timing measurement] TB to check effect of IR drop on arc setup time and hold time from dly_sel<8:0> to dly_update |  |
| lcdl_top_timi_arc_ir_drop.bbSim | [For Timing measurement] TB to check effect of IR drop on timing arcs: dly_in àdly_out dti àdto cal_clk àcal_out |  |
| lcdl_top_timi_max_tran_out.bbSim | [For Timing measurement] TB to check max transition output for pins: dly_out, cal_out, dto, atpg_so |  |

### Definition of Spec Parameters

- Step size (avg) or LSB = (D(lock code) – D(0))/lock code where D(lock code) is the rise delay at tap corresponding to lock code at a particular frequency and D(0) is the rise delay at tap 0.
- DNL (max|min) = {(max|min) [D(n+1) - D(n) - LSB]} where DNL(max) is the max positive DNL over the lock code range and DNL(min) is the max negative DNL over the lock code range and LSB is the average step size calculated over the lock code range.
- INL (max) = max [D(n)- LSB*n-D(0)] is the max INL over the lock code range where D(n) is the delay at tap n and D(0) is the delay at tap 0 and LSB is the average step size calculated over the lock code range.
- Step size (max) = max [D(n+1) – D(n)] is the max step size over the lock code range. (positive step size means LCDL is monotonic and negative step size means LCDL is non-monotonic)
- 1st/2nd edge offset = difference in the rise delay between 1st rise edge and 2nd rise edge measured at dly_out.
- Insertion delay= total delay from dly_in -> dly_out at tap 0.
- LCDL total delay(min) @tap511= the fastest delay through the LCDL corresponding to D(511)-D(0). The inverse of this defines the lowest frequency we can lock to.
- DCD = the duty cycle distorting through the LCDL due to monte and ageing.
- Decoding speed (max) = slowest decoding speed while changing the code from a to b (could be any code from 0 -> 511), applies to both the coarse decoder and fine decoder.
- Calibration Offset = the offset of the delay at calibrated code and the expected delay.
### Performance Specifications

| **Parameter** | **Min** | **Max** | **Units** | **Remark** |
| --- | --- | --- | --- | --- |
| Locking Frequency | 2000 | 8000 | MHz | The supported frequency for mission mode locking delay (delay at lock_code). |
| 1T Calibration Frequency | 4000 | 8000 | MHz | The supported frequency for 1T calibration mode(code 1T). |
| 0.5T Calibration Frequency | 2000 | - | MHz | The supported frequency for 0.5T calibration mode(code 0.5T). |
| Step size (avg) or LSB | - | 2 | ps | MC 3 sigma |
| Insertion Delay | - | 187.5 | ps | (1.5T) Consistency with Phase delay update timing constraints |
| Decoder Delay | - | 312 | ps | (2.5T) Consistency with Phase delay update timing constraints. |
| DNL | - | 1 | ps | None MC (0.5*LSB) |
|  | - | 3 | ps | MC 3 sigma (1.5*LSB) |
| INL | - | 2 | ps | None MC, 1*LSB |
|  | - | 4 | ps | MC 3 sigma, 2*LSB |
| 1T Calibration Offset | - | 12.5 | ps | MC 3 sigma, (10%*1T) (timing budget from TOPSIM) |
| 0.5T Calibration Offset | - | 15 | ps | MC 3 sigma, (8%*0.5T) (input duty cycle 50%) (confirmed by timing budget from TOPSIM that include the calibration offset with 50% DCin and MPW of cal_clk at 2Ghz) |
| Leakage current | - | 50 | uA | TT,VDD, 25C, at lock_code |
| Active current | - | 2 | mA | TT,VDD, 25C, at lock_code |
| Step size (max) | - | 3 | ps | None MC [1.5*LSB] |
|  | - | 4 | ps | MC [2*LSB] |
| DCD | - | 2 | % | None MC Full code with 50% input duty cycle |
|  | - | 3 | % | None MC From code 32 to lock_code+8 with worst case input duty cycle. |
|  | - | 5 | % | MC 3 sigma at code 0 (The spec is from clktree team) |
|  | - | 2 | % | MC 3 sigma: The DCD variation in range code 0->8 This value will be count into Link margin |
|  | - | 5 | % | MC 3 sigma at code 0x20 (The spec is from clktree team) |
|  | - | 2 | % | MC 3 sigma: The DCD variation in range code 32-> lock_code This value is will be count into the MPW of reciever clocks. |
| Train error | - | 5 | ps | MC 3sigma, Strobe training alignment error.(8%*UI) (spec from TOPSIM) This value will be count into Link margin |
| Supply Noise Induced Jitter | - | 0.5 | ps/mV | Tap lock_code |
| Temperature Drift Induced Jitter | - | 0.1 | ps/oC | Tap lock_code |

# dwc_ucie2phy_lcdlsim

## Overview

dwc_ucie2phy_lcdlsim is a stripped-down version of lcdl to provide the adjustable clock delay for Signal Integrity Monitor (SIM) block. The unnecessary features are removed to save area and insertion delay.

This macro operates under a regulated supply which its level is larger than the core supply, so all interface signals (except dly_in and dly_out) are shifted up with built-in level shifter.

There is a synchronous built-in clock gater, user can turn off clock.

## Cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_lcdlsim_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_lcdlsim_ew | Support UCIe-A/S, EW PHY orientation |

## Features

- Power supply at IP port:
- Core voltage: 0.75v +/-10%.
- Regulated supply: 0.85v +/-10%
- Junction operation temperature:
- Performance range: -40oC to 125oC.
- EM: 10 years, 105oC with self-heating considered, 0.75V + 10% power supply.
- Clock frequency support: 2GHz - 8GHz.
- Precise adjustment step: Less than 2ps (32 steps in 1UI).
- Built-in clock gater.
- Built-in scan chain for the control logic.
- Provide 1007 delay step settings via 19bit input port configuration.
- Glitchless that allows updating code on the flight.
## Block diagram

Figure 21 Block diagram of lcdlsim

## Pin list

Figure 22 lcdlsim pin list

| **Pin Name** | **Direction** | **Power Domain** | **Clock Domain** | **Frequency** | **Function** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | VDD | - | - | Core power supply |
| VDDREG | Input | VDDREG | - | - | Regulated supply |
| VSS | Input | 0 | - | - | Ground |
| clk0 | Input | VDDREG | Self | 8 GHz | Dummy pin for feature usage, no function |
| clk90 | Input | VDDREG | Self | 8 GHz | Dummy pin for feature usage, no function |
| clk180 | Input | VDDREG | Self | 8 GHz | Delay Line Input: Input signal to be delayed. |
| clk270 | Input | VDDREG | Self | 8 GHz | Dummy pin for feature usage, no function |
| dly_update | Input | VDD | Self | 2 GHz | Clock for the delay line delay select (dly_sel) flops |
| dly_out | Output | VDDREG | dly_in | 8 GHz | Delay Line Output |
| clken | Input | VDD | Async | - | Clock gater enable signal |
| force_low | Input | VDD | Async | - | Force dly_out to zero |
| resetn | Input | VDD | Async | - | Asynchronous reset |
| atpg_mode | Input | VDD | - | - | Scan mode: when asserted, the dly_sel flops are in scan mode |
| atpg_se | Input | VDD | - | - | dly_sel flops scan chain enable |
| atpg_si | Input | VDD | - | - | dly_sel flops scan chain input |
| atpg_so | Output | VDD | - | - | dly_sel flops scan chain output |
| force_max_delay | Input | VDD | Async | - | Force dly_sel bits to high for burn-in |
| dly_mux_sel_even[2:0] | Input | VDD | dly_update |  | 000 = even coarse mux 0-7 001 = even coarse mux 8-15 010 = even coarse mux 16-23 011 = even coarse mux 24-31 100 = even coarse mux 32-39 101 = even coarse mux 40-47 110 = even coarse mux 48-55 111 = even coarse mux 56-63 |
| dly_mux_sel_odd[2:0] | Input | VDD | dly_update |  | 000 = odd coarse mux 0-7 001 = odd coarse mux 8-15 010 = odd coarse mux 16-23 011 = odd coarse mux 24-31 100 = odd coarse mux 32-39 101 = odd coarse mux 40-47 110 = odd coarse mux 48-55 111 = odd coarse mux 56-63 |
| dly_sel_crs_even[3:0] | Input | VDD | dly_update |  | Delay line select for the even coarse delay backward muxes |
| dly_sel_crs_odd[3:0] | Input | VDD | dly_update |  | Delay line select for the odd coarse delay backward muxes |
| dly_sel_fine[4:0] | Input | VDD | dly_update |  | Delay line select for the fine delay 16 bits interpolator |

## DFT and RTL constraints

They are similar to LCDL.

In DFT mode, set force_low = 1 to tie dly_out to zero.
