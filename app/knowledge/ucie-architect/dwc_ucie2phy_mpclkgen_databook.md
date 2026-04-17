**DesignWareCore ****UCIE**** PHY**

Data book

UCIE2 PHY Multi-Phase Clock Generation

dwc_ucie2phy_mpclkgen

Version

, 202

Copyright Notice and Proprietary Information Notice

Copyright © 202 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

Destination Control Statement

All technical data contained in this publication is subject to the export control laws of the United States of America. Disclosure to nationals of other countries contrary to United States law is prohibited. It is the reader's responsibility to determine the applicable regulations and to comply with them.

Disclaimer

SYNOPSYS, INC., AND ITS LICENSORS MAKE NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS MATERIAL, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Trademarks

Synopsys and certain Synopsys product names are trademarks of Synopsys, as set forth at

All other product or company names may be trademarks of their respective owners.

Synopsys, Inc.690 E. Middlefield RoadMountain View, CA 94043

Contents

3.4.3 DLL Comp DAC Decoder

3.5 Calibration and Adaptation Algorithms

3.5.1 Top-Level Calibration Algorithm Sequence

3.5.2 Initialization of DLL codes before Calibration

3.5.3 DLL Phase Detector Offset Calibration

3.5.4 DLL Delay-Line Mission Calibration

3.5.5 DLL Calibration of track temperature drift

3.5.6 vote_result

3.5.7 vote_result_initcal

3.6 Clock pause

4 RTL and Timing Constraints

4.1.1 Settling time for mission mode and calibration mode

4.1.2 Sample Time in Comparator Offset Calibration Mode

4.1.3 Sample Time in Mission mode

4.1.4 Settling time from pclk static-to-toggle to output mux before enabled clock-gater

4.1.5 Settling time for DLL ac_en from ac_en toggle to resumed mission

4.1.6 IDDQ measurement

4.1.7 Logical configurations for low/high data rate

4.1.8 DFT

4.1.9 Burn-in recommendation.

4.1.10 Anti-Aging recommendation.

4.1.11 Phase detector behavior

5 Electrical Parameters

5.1 Top Electrical Parameters

5.2 Blocks Electrical Parameters

5.3 DC Specification

5.4 AC Specification

5.5 Power Specification

6 Simulation Results

6.1 Simulation Results vs. Specification

6.2 EMIR Results

7 Simulation Plan

7.1 Corners & verification conditions

7.2 Test-benches list

8 Integration Guideline

9 Changes from Reference Design

**List ****o****f Figures**

Figure 37 Flowchart showing top-level startup calibrations

Figure 38 DLL PD Offset FSM Calibration

Figure 39 DLL Delay-Line Initialization Calibration

Figure 310 DLL Delay-Line Leg Calibration

Figure 311 DAC Coarse Calibration

Figure 312 DAC VREG Calibration

Figure 313 zcal_vote (vote_result) block diagram

Figure 314 zcal_vote (vote_result_initcal) block diagram

Figure 315 Operation waveform of clock pause

Figure 41 DLL Power-Up & Power-Down Sequence

Figure 42 Settling time from Ramp Up

Figure 43 Sample time in comparator offset calibration mode

Figure 44 Sample time in Mission mode

Figure 45 Settling time from pclk static-to-toggle to output mux

Figure 46 Settling time for DLL ac_en from ac_en toggle to resumed mission

**List ****o****f Tables**

Table 35 Comparator offset compensation DAC decoder

Table 36 zcal_vote (for vote_result)

Table 37 zcal_vote (for vote_result_initcal)

Table 41 RTL and timing requirements

Table 42 IDDQ measurement condition

Table 43 High data rate Conditions.

Table 44 Low data rate Conditions.

Table 45 DFT setting

Table 46 Burn-in test condition.

Table 47 Anti-Aging Conditions.

Table 48 PD Behavior with input phase range

Revision History

| Version | Date | Author |  | Change Description |
| --- | --- | --- | --- | --- |
| 0.1 | Jan 01, 2024 | Tuan Pham |  | Initial Version. |
| 0.2 | Feb 27, 2024 | Tuan Pham |  | Update Block Diagram, Pin list. |
| 0.3 | Apr 12, 2024 | Tuan Pham |  | Update section 3.4 DLL Decoders & section 3.5 Calibration and Adaptation Algorithms. |
| 0.4 | May 09, 2024 | Tri Vo |  | Change power pin name: vdd VDD gd VSS vreg_vp VREG_VP |
| 0.5 | Jun 18, 2024 | Tuan Pham |  | Update True-Table at section 3.4.2 & 3.4.3. Update section 3.3 Pin Description. Update section 4 RTL and Timing Constraints |
| 0.6 | Jun 18, 2024 | Tuan Pham |  | Update section 3.5 Calibration and Adaptation Algorithms Add IDDQ and Burn-in test condition |
| 0.7 | July 18, 2024 | Tuan Pham |  | Create section 3.1.1 DW Clocking Scheme for wide range of data rate (4Gbps-40bps) Update 3.3 Pin Description Update Figure 3 6 ac-coupling diagram. Update Figure 3 7 Flowchart showing top-level startup calibrations. Update Figure 3 10 DLL Delay-Line Leg Calibration Create section 4.1.7 Anti-Aging recommendation. |
| 0.8 | Aug 06, 2024 | Tuan Pham |  | Update correctly Table 3 1 Data Rate Range Conditions. Figure 3 2 MPCLKGEN phase gen with wide range data rate diagrams - with added pin freqsel_reset. Update 3.3 Pin Description with added pin freqsel_reset. Update Table 4 1 RTL and timing requirements for items DLLOffsetSampleTime & DLLMissionSampleTime. Update 3.5.5 DLL Calibration of track temperature drift with notes only step=1 only used in this mode. Create 4.1.6 Logical configurations for low/high data rate Update Table 4-6 Anti-Aging Conditions. Create 4.1.9 Phase detector behavior |
| 0.81 | Aug 07, 2024 | Tuan Pham |  | Update 3.3 Pin Description with rename freqsel_reset into resetn. Update 4.1.7 Burn-in recommendation. Update 4.1.8 Anti-Aging recommendation. |
| 0.9 | Sep 23, 2024 | Tuan Pham |  | Add pin dll_clkgt_en & dll_clkgt_resetn Update Figure 3 2 MPCLKGEN phase gen with wide range data rate diagrams with the added pins.Update section 3.3 Pin Description with the added pins. |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

Reference Documents

# Introduction

This document describes the function and implementation of dll-based multiple phase clock generation for high-speed application. It converts a single-phase clock input to 4-phase clock.

# Overview

2

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |

## Input Specification

Table 2 Input Specification

| Parameter | Specification | Note |
| --- | --- | --- |
| UCIe Standard | 2.0 |  |
| Max Speed | 2GHz – 10GHz |  |
| VDDREG **(Pin **VREG_VP** for TC Aug)** | 0.85 +/-5% |  |
| VDD | 0.75 +/-10% |  |

## Recommended operation condition

Table 2 Recommended operation condition

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VDDREG | Regulate Power Supply | 0.8075 | 0.85 | 0.8925 | V |
| VDD | Core Power Supply | 0.675 | 0.75 | 0.825 | V |
| VSS | Ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction temperature | -40 | 25 | 125 | C |

# Functional Outline

## Functions and Features

### DW Clocking Scheme for wide range of data rate (4Gbps-40bps)

PHY needs to support wide range data rate: 4Gbps to 40Gbps. Quadrature clocking scheme is supported in both TX and RX side. And 4-phase clock gen (mpclkgen) is required to convert single phase to 4-phase clock, but mpclkgen only operates well in high frequence 4GHz – 10GHz, is really challenging for lower 4Ghz. That comes to supporting clocking DIV2 after clock gater for low data rate & shown in below diagrams. FIFO, calibration, training, … is consistent from 4Gbps to 40Gbps. And, in high level, clocking scheme is half rate, but the internal Tx/Rx side is still quarter rate.

Figure 31 DW Clocking Scheme

Figure 32 MPCLKGEN phase gen with wide range data rate diagrams

Table 3 Output frequency range

| FreqSel | Output frequency range (GHz) | Note |
| --- | --- | --- |
| 1 | < | The output clock frequency is of the input clock |
| 0 | - 10 | The output clock frequency is the same as the input clock |

Note:

- User needs to configure freqsel pin based on the target data rate.
### DLL MPCLKGEN

The multi-phase clock generation (mpclkgen) as delay-locked loop (DLL) generates eight phases clocks which have a 45-degree phase relationship, and four phases clocks which have a 90-degree phase relationship to the adjacent phase to Write Clock-Tree.

The block diagram of mpclkgen block is given below

Figure 33 High level block diagram

## MPCLKGEN Architecture and Implementation

The delay line has eight stages. The first stage AC-couples the high-speed clock signal level-shifting it to the VREG_DLL voltage domain. The next delay stages generate the clocks used for the clock path. The final stage is used to generate CAL clock for phase detector calibration, and to provide uniform loading to all stages. The delay-line is first calibrated and then an FSM closes the loop. The delay in controlled in two ways: first by controlling the number of legs enabled in the delay stages and secondly by controlling the supply-voltage for the delay stages. The supply voltage for the delay stages is called VREG_DLL and is set via a regulator. The reference for the VREG_DLL regulator is controlled by a dedicated voltage DAC.

Figure 34 Delay Line block diagram

Figure 35 mpclkgen dll clock path

Ac-coupling diagram are shown in below.

Figure 36 ac-coupling diagram.

During DLL delay calibration firstly the number of legs in the delay stages is calibrated. Secondly the DLL FSM is enabled, and this controls the VDAC code in order to fine-tune the delay through the delay line. The sense point for the calibration is phase detector which takes two clocks with 360-degree phase gap; they pre_ph135 and ph135 in this project. The phase detector is first calibration by putting a common-clock CAL into both inputs of the phase detector.

At the output of the delay stages there are AC-coupled level-shifters in order to move from the VREG_DLL voltage domain to the VREG_VP voltage domain. In the transmitter there are additional current DACs to implement duty-cycle correction for certain phases using the AC-coupled level-shifters, however in the RC this is not done. The AC-coupled level-shifters themselves provide significant duty-cycle correction.

## Pin Description

Table 3 Pin list

| Pin name | Direction | Type | Power Domain | Clock | Description |
| --- | --- | --- | --- | --- | --- |
| **dll_pll_clk_in** | input | Clock | VDD | - | High-speed PLL clock |
| **ph_0_drv** | output | Clock | VDD | dll_pll_clk_in | DLL output clock phase 0 degrees for driver |
| **ph_90_drv** | output | Clock | VDD | dll_pll_clk_in | DLL output clock phase 90 degrees for driver |
| **ph_180_drv** | output | Clock | VDD | dll_pll_clk_in | Unused, tied low internally |
| **ph_270_drv** | output | Clock | VDD | dll_pll_clk_in | Unused, tied low internally |
| **freqsel** | Input | Digital | VDD | - | Data Rate Range Control 1’b0 High Data Rate. The output clock frequency is the same as the input clock. 1’b1 Low Data Rate. The output clock frequency is a half of the input clock. |
| **reset****n** | Input | Digital | VDD | - | Asynchronous reset pin for Flipflops/latches in low data-rate path. 1’b0 Reset Mode 1’b1 Enable Paths |
| **d****l****l_clk****gt****_en** | Input | Digital | VDD | - | Clock gater enable. It is connected to iclk0 synchronizer (sync6) before going to clock gater. |
| **d****l****l_clkgt_pause** | Input | Digital | VDD | - | Clock gater enable/pause. It is connected to iclk90 synchronizer (sync6) before going to clock gater. |
| **d****l****l_clk****gt****_****se** | Input | Digital | VDD | - | Clock gater scan enable. It enables clock gater without synchronizer |
| **d****l****l_clk****gt****_resetn** | Input | Digital | VDD | - | Asynchronous resetn pin for clock gater synchronizer (sync6) |
| **dll_ac_en** | input | Digital | VDD | - | Enable the AC coupled stage de-skew cell for the delay_line |
| **dll_vreg_en** | input | Digital | VDD | - | enable the VREG_DLL |
| **dll_vreg_byp** | input | Digital | VDD | - | enable a bypass for the VREG_DLL |
| **dll_delay_leg_en****[2:0]** | input | Digital | VDD | - | value for the delay_line leg enable control |
| **dll_vreg_dac_coarse_code****[8:0]** | Input | Digital | VDD | - | coarse code to latch into the VREG DAC |
| **dll_vreg_dac_coarse[1:0]** | input | Digital | VDD | - | coarse control the vcm of the VREG DAC |
| **dll_vreg_dac_coarse_range[1:0]** | input | Digital | VDD | - | coarse control the range of the VREG DAC |
| **dll_vreg_dac_code****[8:0]** | input | Digital | VDD | - | fine code to latch into the VREG DAC |
| **dll_vreg_dac_range[1:0]** | input | Digital | VDD | - | fine control the range of the VREG DAC |
| **dll_vreg_dac_en** | input | Digital | VDD | - | enable for the VREG DAC |
| **dll_comp_dcc_dac_code[8:0]** | input | Digital | VDD | - | code for comparator offset DAC code and DCC DAC code |
| **dll_comp_dac_range[1:0]** | input | Digital | VDD | - | range control for the comparator offset DAC |
| **dll_comp_dac_vcm[1:0]** | input | Digital | VDD | - | Code for the comparator offset DAC |
| **dll_comp_dcc_dac_en** | input | Digital | VDD | - | Enable for the comparator offset DAC and DCC DAC |
| **ibias_dll_dacs** | Input | Digital | VDD | - | Bias current for the DLL vDACs |
| **dll_phd_ana_sel[4:0]** | input | Digital | VDD | - | Control for phase detector ANA MUX Default value: 5’d0 |
| **dll_phd_dig_sel[4:0]** | input | Digital | VDD | - | control for phase detector high-speed clock MUX selection 5’d0 – Delay Line Cal 5’d1 - Offset Cal |
| **dll_phd_en** | input | Digital | VDD | - | enable for phase detector |
| **dll_phd_comp_in_clk** | input | Clock | VDD | - | input clock for phase detector comparator |
| **dll_phd_comp_out_clk** | output | Clock | VDD | dll_phd_comp_in_clk | buffered version of dll_phd_clk |
| **dll_phd_early_late** | output | Digital | VDD | dll_phd_comp_in_clk | phase detector output |
| **VDDREG** | Input | Power | VDDREG | - | DLL VREG supply voltage |
| **VDD** | Input | Power | VDD | - | DLL CORE supply voltage |
| **VSS** | input | Gound | VSS | - | Common ground |

## DLL Decoders

### DLL Leg Decoder

Table 3 DLL leg decoder

| Input | Output (thermo decoder) |
| --- | --- |
| dll_delay_leg_en[0:2] | dll_leg_th_en[0:5] = [6:11] = … [54:59] |
| 000 | 000000 |
| 001 | 000001 |
| 010 | 000011 |
| 011 | 000111 |
| 100 | 001111 |
| 101 | 011111 |
| 110 | 111111 |
| 111 | 111111 |

Signals dll_leg_th_en_n[0:59] are inverted versions of dll_leg_th_en[0:59]

### DLL VREG DAC decoder

This block implements a binary to thermometer decoder for the VDACs and DLL IDACs in the DLL. There are also some decoders for the range control. There are two separate interfaces, one for the comparator offset, and the other for the DLL voltage reference.

Table 3 DLL Vref DAC decoder

| Input | Output (Output = input) |
| --- | --- |
| dll_vreg_dac_coarse_code[3:0] | vreg_dac_coarse_bin[3:0] |
| 0001 | 0001 |
| 0010 | 0010 |
| 0100 | 0100 |
| 0101 | 0101 |
| 0110 | 0110 |
| 0111 | 0111 |
| 1000 | 1000 |
| 1001 | 1001 |
| 1010 | 1010 |
| 1011 | 1011 |
| 1100 | 1100 |
| 1101 | 1101 |
| 1110 | 1110 |
| 1111 | 1111 |

| Input | Output (thermo decoder) |
| --- | --- |
| dll_vreg_dac_coarse_code[8:4] | vreg_dac_coarse_th[30:0] |
| 00000 | 0000…0000 |
| 00001 | 0000…0001 |
| 00010 | 0000…0011 |
| 00011 | 0000…0111 |
| … | … |
| 11101 | 0011…1111 |
| 11110 | 0111…1111 |
| 11111 | 1111…1111 |

| Input | Output (output = input) |
| --- | --- |
| dll_vreg_dac_code[3:0] | vreg_dac_bin[3:0] |
| 0001 | 0001 |
| 0010 | 0010 |
| 0100 | 0100 |
| 0101 | 0101 |
| 0110 | 0110 |
| 0111 | 0111 |
| 1000 | 1000 |
| 1001 | 1001 |
| 1010 | 1010 |
| 1011 | 1011 |
| 1100 | 1100 |
| 1101 | 1101 |
| 1110 | 1110 |
| 1111 | 1111 |

| Input | Output (thermo decoder) |
| --- | --- |
| dll_vreg_dac_code[8:4] | vreg_dac_th[30:0] |
| 00000 | 0000…0000 |
| 00001 | 0000…0001 |
| 00010 | 0000…0011 |
| 00011 | 0000…0111 |
| … | … |
| 11101 | 0011…1111 |
| 11110 | 0111…1111 |
| 11111 | 1111…1111 |

| Input | Output (thermo decoder, inverted) |
| --- | --- |
| dll_vreg_dac_coarse_range[1:0] | vreg_dac_coarse_range_th_n[2:0] |
| 00 | 000 |
| 01 | 001 |
| 10 | 011 |
| 11 | 111 |

| Input | Output (one hot decoder, inverted) |
| --- | --- |
| dll_vreg_dac_coarse[1:0] | vreg_dac_coarse_1hot_n[3:0] |
| 00 | 0000 ( current circuit decoder: 0000; Expected circuit decoder: 1110, both cases are acceptable with circuit performance since LSB [0] = 0) |
| 01 | 1101 |
| 10 | 1011 |
| 11 | 0111 |

| Input | Output (thermo decoder, inverted) |
| --- | --- |
| dll_vreg_dac_range[1:0] | vreg_dac_range_th_n[2:0] |
| 00 | 000 |
| 01 | 001 |
| 10 | 011 |
| 11 | 111 |

### DLL Comp DAC Decoder

Table 3 Comparator offset compensation DAC decoder

| Input | Output (Output = Input) |
| --- | --- |
| dll_comp_dcc_dac_code[3:0] | comp_dac_bin[3:0] |
| 0001 | 0001 |
| 0010 | 0010 |
| 0011 | 0011 |
| 0101 | 0101 |
| 0110 | 0110 |
| 0111 | 0111 |
| 1000 | 1000 |
| 1001 | 1001 |
| 1010 | 1010 |
| 1011 | 1011 |
| 1100 | 1100 |
| 1101 | 1101 |
| 1110 | 1110 |
| 1111 | 1111 |

| Input | Output (thermo decoder) |
| --- | --- |
| dll_comp_dcc_dac_code[8:4] | comp_dac_th[30:0] |
| 00000 | 0000…0000 |
| 00001 | 0000…0001 |
| 00010 | 0000…0011 |
| 00011 | 0000…0111 |
| … | … |
| 11101 | 0011…1111 |
| 11110 | 0111…1111 |
| 11111 | 1111…1111 |

| Input | Output (one hot decoder, inverted) |
| --- | --- |
| dll_comp_dac_vcm[1:0] | comp_dac_vcm_1hot_n[3:0] |
| 00 | 0000 ( current circuit decoder: 0000; Expected circuit decoder: 1110, both cases are acceptable with circuit performance since LSB [0] = 0) |
| 01 | 1101 |
| 10 | 1011 |
| 11 | 0111 |

| Input | Output (thermo decoder, inverted) |
| --- | --- |
| dll_comp_dac_range[1:0] | comp_dac_range_th_n[2:0] |
| 00 | 000 |
| 01 | 001 |
| 10 | 011 |
| 11 | 111 |

## Calibration and Adaptation Algorithms

### Top-Level Calibration Algorithm Sequence

The sequence for DLL startup & calibrations is shown in the below flowchart. The following sections go into each block of calibrations in detailed.

Figure 37 Flowchart showing top-level startup calibrations

### Initialization of DLL codes before Calibration

Below are initialization DLL Codes before Offset Calibration or Mission Delay-Line Calibration.

The table is organized with operating frequency & projects.

#### Table of Code for project SF4 H200

Common settings for full range frequency 10Ghz to 4GHz clock.

| Output frequency (GHz) | Pin | Value | **Note** |
| --- | --- | --- | --- |
| From 4 to 10 | dll_delay_leg_en[2:0] | 3’d6 |  |
|  | dll_vreg_dac_coarse_code[8:0] | 9'd0 |  |
|  | dll_vreg_dac_coarse_range[1:0] | 2'd3 |  |
|  | dll_vreg_dac_range[1:0] | 2'd1 |  |
|  | dll_comp_dcc_dac_code[8:0] | 9'd255 | Disabled Offset Calibration |
|  | dll_comp_dcc_dac_code[8:0] | 9'd0 | Enable Offset Calibration |
|  | dll_comp_dac_range[1:0] | 2'd3 |  |
|  | dll_comp_dac_vcm[1:0] | 2'd0 |  |

Specific settings with operating frequency

| Output frequency (GHz) | Pin | Value | Note |
| --- | --- | --- | --- |
| 10 | dll_vreg_dac_coarse[1:0] | 2'd0 |  |
|  | dll_vreg_dac_code[8:0] | 9'd64 |  |
| 8 | dll_vreg_dac_coarse[1:0] | 2'd1 |  |
|  | dll_vreg_dac_code[8:0] | 9'd64 |  |
| 6 | dll_vreg_dac_coarse[1:0] | 2'd2 |  |
|  | dll_vreg_dac_code[8:0] | 9'd256 |  |
| 4 | dll_vreg_dac_coarse[1:0] | 2'd3 |  |
|  | dll_vreg_dac_code[8:0] | 9'd256 |  |

#### Table of Code for project TSMCN5 H201

Common settings for full range frequency 10Ghz to 4GHz clock.

| Output frequency (GHz) | Pin | Value | **Note** |
| --- | --- | --- | --- |
| From 4 to 10 | dll_delay_leg_en[2:0] | 3’d6 |  |
|  | dll_vreg_dac_coarse_code[8:0] | 9'd0 |  |
|  | dll_vreg_dac_coarse_range[1:0] | 2'd3 |  |
|  | **dll_vreg_dac_range[1:0]** | **2'd1** |  |
|  | dll_comp_dcc_dac_code[8:0] | 9'd255 | Disabled Offset Calibration |
|  | dll_comp_dcc_dac_code[8:0] | 9'd0 | Enable Offset Calibration |
|  | dll_comp_dac_range[1:0] | 2'd3 |  |
|  | dll_comp_dac_vcm[1:0] | 2'd0 |  |

Specific settings with operating frequency

| Output frequency (GHz) | Pin | Value | Note |
| --- | --- | --- | --- |
| 10 | dll_vreg_dac_coarse[1:0] | 2'd0 |  |
|  | dll_vreg_dac_code[8:0] | 9'd64 |  |
| 8 | dll_vreg_dac_coarse[1:0] | 2'd0 |  |
|  | dll_vreg_dac_code[8:0] | 9'd64 |  |
| 6 | dll_vreg_dac_coarse[1:0] | 2'd1 |  |
|  | dll_vreg_dac_code[8:0] | 9'd256 |  |
| 4 | dll_vreg_dac_coarse[1:0] | 2'd2 |  |
|  | dll_vreg_dac_code[8:0] | 9'd256 |  |

### DLL Phase Detector Offset Calibration

The offset of the phase detector must be calibrated in order for the DLL to be able to accurately lock.

The phase detector is setup in order to input two identical clocks into the phase detector. Design will select internal ph_call signals to both ports of PD phases for offset calibration by setting dll_phd_dig_sel<4:0> = 5’d1.

The DLL comparator offset calibration is described in below figure.

Figure 38 DLL PD Offset FSM Calibration

### DLL Delay-Line Mission Calibration

Next, the mission delay line is calibrated.

The calibration controls the number of legs in each delay cell, and also the range and common-mode level of the VREG VDAC. The DLL phase detector is set to its nominal state, with the 0 degree and 360 degree clocks being input to the phase detector.

The output of the phase detector is observed, and the leg and DAC controls are searched in order to find the optimal settings for the DLL.

DLL Delay-Line calibration flow is described as below.

Figure 39 DLL Delay-Line Initialization Calibration

Figure 310 DLL Delay-Line Leg Calibration

Figure 311 DAC Coarse Calibration

Figure 312 DAC VREG Calibration

### DLL Calibration of track temperature drift

In real time calibration, DLL support **combo DAC Coars****e Calibration & then, DAC ****VREG Calibration** in-order to Temp Drift Calibration which is auto real time calibration to correct phase mismatch due to V/T drift.

*Note that ****only step = 1**** applies in this combo DAC Coarse & VREG calibration during VT drift to avoid unexpected glitches.*

Initialization Calibration and LEG Calibration are not needed & disable in this mode.

### vote_result

The **vote_result** is referred exactly to section 3.10 “zcal_vote Design Description” on the document . Below are sub-sections printed out from document.

RTL team please help to review & feedback.

#### Interface Specification

Below Table lists the pinout for the zcal_vote (vote_result) module.

Table 3 zcal_vote (for vote_result)

| **Pin Name** | **Direction** | **Width** | **Description** |
| --- | --- | --- | --- |
| **CSR** |  |  |  |
| csrZCalNumVotes | Input | 3 | Number of consecutive output bits over which majority voting is done during the search algorithm: - 0 = 1. - 1 = 9. - 2 = 17. - 3 = 33. - 4 = 65. - 5 = 129. - 6 = 193. - 7 = 255. |
| **Internal ZCAL controls** |  |  |  |
| zcal_comp_out | Input | 1 | Impedance calibration comparator output. |
| vote_en | Input | 1 | Activates the zcal_vote module |
| vote_result | Output | 1 | Returns the result of the vote |
| vote_vld | Output | 1 | Indicates the vote_result is valid |

For our FSM MPCLKGEN connections, the mpclkgen output phase detector *dll_phd_early_late* pin will be connected to pin *zcal_comp_out*.

#### Functional Specification

This block consists of three counters and some logic to sample and count 1s and 0s received on zcal_comp_out. The vote_result is set to a 1 if the count of 1s is greater than the count of 0s. The total number of samples taken is determined by csrZCalNumVotes. A vote counter counts down from this value when vote_en is asserted and the vote_done signal is asserted when the counter reaches 0. The vote counter resets to csrZcalNumVotes when vote_en is 0. When the vote counter reaches 0, it stays at 0 until vote_en is deasserted. The 1s and 0s counters are enabled when vote_en is asserted. The 1s and 0s counters reset to 0 when vote_en is 0. The figure below shows the zcal_vote block diagram.

Figure 313 zcal_vote (vote_result) block diagram

### vote_result_initcal

The **vote_result****_initcal ****function **is slightly modified from the vote_result function. The functions is only supported during **DLL Delay-Line Initialization Calibration****.**** **The function is to help the early_late signal to work well even it toggles during dead-zone phase detector phase.

Other calibrations (DLL Delay-Line Leg Calibration, DAC Coarse Calibration, DAC VREG Calibration, Phase Detector Offset Calibration) still use the vote_result.

#### Interface Specification

Below Table lists the pinout for the zcal_vote (vote_result_initcal) module.

Table 3 zcal_vote (for vote_result_initcal)

| **Pin Name** | **Direction** | **Width** | **Description** |
| --- | --- | --- | --- |
| **CSR** |  |  |  |
| csrZCalNumVotes | Input | 3 | Number of consecutive output bits over which majority voting is done during the search algorithm: - 0 = 1. - 1 = 9. - 2 = 17. - 3 = 33. - 4 = 65. - 5 = 129. - 6 = 193. - 7 = 255. |
| csrZCalNumThres | Input | 2 | New added CSR to control threshold values for event of count1&count0. - 0 = 0 - 1 = 1 - 2 = 2 - 3 = 3. |
| **Internal ZCAL controls** |  |  |  |
| zcal_comp_out | Input | 1 | Impedance calibration comparator output. |
| vote_en | Input | 1 | Activates the zcal_vote module |
| vote_result | Output | 1 | Returns the result of the vote |
| vote_vld | Output | 1 | Indicates the vote_result is valid |

#### Functional Specification

The vote_result is set to a 0 if the count of 1s & the count of 1s are greater csrZCalNumThres; otherwise, the vote_result is set to a 1 if the count of 1s is greater than the count of 0s.

Figure 314 zcal_vote (vote_result_initcal) block diagram

## Clock pause

Pause feature is used to pause for one clock cycle whenever dll_clkgt_pause goes from low to high. The operation is described as below waveform. dll_clkgt_pause need to be high at least 6 pclk cycles.

Figure 315 Operation waveform of clock pause

# RTL and Timing Constraints

The power up/power down sequence for the DLL is provided as below.

Figure 41 DLL Power-Up & Power-Down Sequence

Table 4 RTL and timing requirements

| **Parameter** | **Symbol** | **Value****(Min)** | **Value****(Max)** | **Unit** | **Note** |
| --- | --- | --- | --- | --- | --- |
| Settling Time(Wait time after enabling sub-blocks) | DLLSettleInitial | 500 |  | ns |  |
| Offset sample time in offset calibration mode | DLLOffsetSampleTime | 75 |  | ns |  |
| Comparator sample time in mission mode | DLLMissionSampleTime | 75 |  | ns |  |
| Settling time from pclk static-to-toggle to output mux before enabled clock-gater | DLLSettlingPclkStatictoToggle | 64*Pclk |  |  |  |
| Settling time for DLL ac_en from ac_en toggle to resumed mission | DLLAcenSettle | 64*Pclk |  |  |  |

### Settling time for mission mode and calibration mode

A minimum wait time (DLLSettleInitial) is needed when entering the offset calibration or main mission calibration mode, so that the key analog signals are ready. These changes can happen due to the following scenarios:

- Power ramp up done to Offset calibration mode.
- Power ramp up done to Mission mode (In case of disabled offset).
So, this wait time needs to be observed from all of the above events (from whichever happens latest if they are in sequence) to the first valid sampling edge of dwc_ucie2phy_mpclkgen/dll_phd_comp_in_clk.

Figure 42 Settling time from Ramp Up

### Sample Time in Comparator Offset Calibration Mode

In offset calibration mode, a minimum wait time (DLLOffsetSampleTime) is needed when change one offset code to another offset code, so that the key analog signals are ready to be sampled by the Sense-Amp.

Figure 43 Sample time in comparator offset calibration mode

### Sample Time in Mission mode

In mission mode, a minimum wait time (DLLMissionSampleTime) is needed when changing one mission calibration code (dll_delay_leg_en/ dll_vreg_dac_coarse_code/ dll_vreg_dac_code) to another code, so that the key analog signals are ready to be sampled by the Sense-Amp.

Figure 44 Sample time in Mission mode

### Settling time from pclk static-to-toggle to output mux before enabled clock-gater

The below figure shows settling time/latency from pclk in static-to-toggle to output mux before enabling clock gater.

Figure 45 Settling time from pclk static-to-toggle to output mux

### Settling time for DLL ac_en from ac_en toggle to resumed mission

The below figure shows settling time/latency from ac_en signal toggle to output clocks stable.

Figure 46 Settling time for DLL ac_en from ac_en toggle to resumed mission

### IDDQ measurement

Table 4 IDDQ measurement condition

| Pin | Value | Description |
| --- | --- | --- |
| freqsel | 0 |  |
| dll_ac_en | 0 | Bypass AC coupling |
| dll_vreg_en | 1 | Disable regulator |
| dll_vreg_byp | 1 | Bypass regulator, vout = VDD |
| dll_phd_en | 0 | Disbale phase detector |
| dll_vreg_dac_en | 0 | Disable IDAC |
| dll_comp_dcc_dac_en | 0 | Disable IDAC |

### Logical configurations for low/high data rate

The recommendation is for logical configurations for low data-rate & high data rate.

Table 4 High data rate Conditions.

| Pin | Value | Description |
| --- | --- | --- |
| **freqsel** | ***0*** | *Enable **high** data-rate. Refer to Table 3 1 Data Rate Range Conditions.* |
| **reset****n** | ***0*** | *Always reset path low data rate in high data rate modes.* |
| **dll_ac_en** | ***1*** | *Bypass AC coupling* |
| **dll_vreg_en** | 1 | Enable* *regulator |
| **dll_vreg_byp** | ***0*** | *Disable **Bypass**.* |
| **dll_phd_en** | 1 | Enable* *phase detector |
| **dll_vreg_dac_en** | 1 | Enable* *IDAC |
| **dll_comp_dcc_dac_en** | 1 | Enable* *IDAC |

Table 4 Low data rate Conditions.

| Pin | Value | Description |
| --- | --- | --- |
| **freqsel** | ***1*** | *Enable **low** data-rate. Refer to Table 3 1 Data Rate Range Conditions.* |
| **reset****n** | ***1*** | *Toggle from 0 to 1 to enable low data rate path.* |
| **dll_ac_en** | ***0*** | *Disable **AC coupling* |
| **dll_vreg_en** | 0 | Disable* *regulator for power savings. |
| **dll_vreg_byp** | ***0*** | *Disable Bypass.* |
| **dll_phd_en** | 0 | Disable* *phase detector |
| **dll_vreg_dac_en** | 0 | Disable Enable* *IDAC |
| **dll_comp_dcc_dac_en** | 0 | Disable* *IDAC |

### DFT

Table 4 DFT setting

| Pin | Value | Description |
| --- | --- | --- |
| freqsel | 0 | Enable high speed path |
| dll_ac_en | 0 | Bypass AC coupling |
| dll_vreg_en | 1 | Enable regulator |
| dll_vreg_byp | 1 | Bypass regulator, regulator output is VDDREG |
| dll_phd_en | 0 | Disable phase detector |
| dll_vreg_dac_en | 0 | Disable IDAC |
| dll_comp_dcc_dac_en | 0 | Disable IDAC |
| dll_delay_leg_en[2:0] | 3’b111 | Maximum leg code |

Note: User must configure the regulator (provides power for Phase gen) into bypass mode or mission mode so that the output level is follow VDD.

### Burn-in recommendation.

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run the mission mode. The supply voltage is raised up and must follow VDD core domain, so the internal regulator must be configured in Bypass mode.

Table 4 Burn-in test condition.

| Pin | Value | Description |
| --- | --- | --- |
| freqsel | **0** | Enable high speed path |
| dll_ac_en | **1** | Enable AC coupling |
| dll_vreg_en | **1** | Enable regulator |
| dll_vreg_byp | **1** | Bypass regulator, regulator output is VDDREG |
| dll_phd_en | 1 | Enable phase detector |
| dll_vreg_dac_en | 1 | Enable IDAC |
| dll_comp_dcc_dac_en | 1 | Enable IDAC |

### Anti-Aging recommendation.

The recommendation is for setting of anti-aging mode.

Table 4 Anti-Aging Conditions.

| Pin | Value | Description |
| --- | --- | --- |
| freqsel | **1** | Enable low data-rate/frequency range |
| dll_ac_en | **0** | Bypass AC coupling |
| dll_vreg_en | 1 | Enable regulator |
| dll_vreg_byp | **1** | Disable Bypass |
| dll_phd_en | 1 | Enable* *phase detector |
| dll_vreg_dac_en | 1 | Enable* *IDAC |
| dll_comp_dcc_dac_en | 1 | Enable* *IDAC |
| dll_delay_leg_en[2:0] | 3’d6 |  |
| dll_vreg_dac_coarse_code[8:0] | 9'd0 |  |
| dll_vreg_dac_coarse[1:0] | 2'd0 |  |
| dll_vreg_dac_coarse_range[1:0] | 2'd3 |  |
| dll_vreg_dac_code[8:0] | 9'd64 |  |
| dll_vreg_dac_range[1:0] | 2'd3 |  |

### Phase detector behavior

The table below shows the behavior of phase detector with different input phase difference between phase 0 degree and phase 360 degree.

Table 4 PD Behavior with input phase range

Note that:

- V(early-late) can be 0 or 1(VDD) (unstable value) in dead-zone region.
- In dead-zone region around 180 degree, v_phd_out_p = v_phd_out_m = VDD value.
- For the dead-zone around 0 degree and 360 degree, it should be |v_phd_out_p – v_phd_out_m| < 2mV.
# Electrical Parameters

## Top Electrical Parameters

## Blocks Electrical Parameters

## DC Specification

## AC Specification

## Power Specification

# Simulation Results

## Simulation Results vs. Specification

## EMIR Results

# Simulation Plan

## Corners & verification conditions

## Test-benches list

# Integration Guideline

# Changes from Reference Design
