**UCIe PHY TX IO**** Analog Hard Macro**

Databook

UCIE Standard

Library: dwc_ucie2phy_io_tx

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
| **Jan 30, 2026** | Tri Vo | 1.75 | Mainband TX, update loopback () |
| **Dec 04, 2025** | Tri Vo | 1.72 | Mainband TX: Update DFT condition (remove TxForceAsync and TxAsyncEn) Block diagram: Remove BE replica Add TX-compatible block diagram Move TxPadRep from BE rep to Serializer Move post-loopback connection from BE replica to the BE main Update table 3-10: TxPadRep = 0 when TxCalEn = 0 Add note “Count up” and “Count down” in section of TX BDL program. |
| **Nov 27, 2025** | Tri Vo | 1.71 | TXSB: change PAD_VIO direction from inout to output () |
| **Jun 25 2025** | Tri Vo | 1.70 | Update FIFO architecture to resolve timing issue () |
| **May 29 2025** | Tri Vo | 1.66 | Update TXCAL block diagram |
| **May 12 2025** | Tri Vo | 1.65 | Update new FIFO arch. Update block diagram Add pin TxDatWrEn[2:0] Update txcal16b Update scan chain info |
| **May 08 2025** | Tri Vo | 1.6 | Remove cell tx8b, txcal8b Change pin name: TxFfeGain[2:0] to TxEqGain[3:0] Add new pin: TxResPuSel[1:0] and TxResPdSel[1:0] Remove pin TxBias and TxVref Change connection and update control logic for post-loopback RX loopback connects to Replica back-end Add OR gate to enable Replica back-end txsb now supports both A/S and NS/EW |
| **Apr 18 2025** | Tri Vo | 1.5 | Update FIFO16 block diagram using in TX |
| **Apr 11 2025** | Tri Vo | 1.4 | Change cell name following the new conventional name rule (support UCIe-A/S, NS/EW phy orientation) New tx cell which supporting 16-bit data bus width Add pin description for TX compliant Clarify the spec item () |
| **Feb 14 2025** | Tri Vo | 1.36 | Update TX_CAL FIFO diagram: remove internal unused pin RdPtr[5:0] |
| **Jan 11 2025** | Tri Vo | 1.35 | Add description for Idle and standby mode TX DFT: add LbEn = 0 as suggested by DFT team |
| **Dec 23**** 2024** | Tri Vo | 1.3 | TX: add pin TxClkCalEn () |
| **Dec 10 2024** | Tri Vo | 1.25 | TX_CAL Update logic of TX_CAL () Add scan chain information TX Update clock calibration flow chart with programmable data pattern (Figure 310) () Add scan chain information |
| **Nov 22 2024** | Tri Vo | 1.2 | Update scan () FIFO update () Remove unused ports: TxVregBg, TxVregBypass TX: update logic of Loopback checker |
| **Nov 01 2024** | Chinh Ngo | 1.12 | TX : Update block diagram at loopback 2 bit counter ( swap 0/1 ) Update note for clock mode : TxFfeGain[2:0] = 3’b000 |
| **Oct ****2****8 2024** | Dao Tran Tri Vo | 1.11 | TX: Update section 3.4.6.6 TxDeskewClk* glitchless control sequence: Add phase decrement timing diagram, update timing constraint from 2*lclk to “1ns”. Update equation for DCA average code calculation. Update BDL parameter |
| **Oct 18 2024** | Chinh Ngo Tri Vo | 1.1 | TX : Update description of Feed forward equalizer Update pattern for quadrature clock mode clock_t Add timing constraint for LbDatInSel TX_CAL: Add phase detector () Rename clock pin name to distinguish Data TX and Clock TX |
| **Oct 10 2024** | Chinh Ngo | 1.0 | TX Remove pin TxDcdOut, TxDcdClkSample, TxDcdOffset[5:0], TxDcdMode[1:0] and add TxPadRep due to support DCD sharing. Add pin LbDatInSel, LbDatIn[3:0], LbFxdDatIn[3:0], LbDeskew[2:0], TxStatus, TxDcdIn for loopback features () Update block diagram for loopback features Update figure 3-5: Serializer + tap gen timing diagram Add section for lane-to-lane deskew and Near-side loopback training Remove cell for dwc_ucie2phy_rxlb |
| **Sep ****21**** 2024** | Chinh Ngo Tri Vo | 0.95 | TX: Update RTL constraint Add pin LbDatOut[3:0] to support localized loopback checker () Update equation of DCA average code New cell to support localized loopback: dwc_ucie2phy_rxlb |
| **Sep 10 2024** | Tri Vo | 0.92 | TX_CAL: Change internal connection: WrDat[3] to data gen, WrDat[7:4] and WrDat[2:0] to static logic 0. |
| **Aug 28 2024** | Tri Vo | 0.91 | TX_CAL: add pin TxResEn |
| **Aug 27 2024** | Hoang Nguyen Tri Vo | 0.9 | TX: Added new pins: TxVregBg TxVregBypass Changed bus width TxDeskewClk0 from [6:0] to [7:0] TxDeskewClk90 from [6:0] to [7:0] TxFfeGain from [3:0] to [2:0] Corrected FIFO block diagram Added section for Majority vote, updated flow chart 3-9 and 3-10 Added section for TxResEn usage Added guideline how to update code TxDeskewClk0 and TxDeskewClk90 () Removed the requirement of BDL adjustment after clock calibration TX_CAL: Changed bus width: TxDeskewClk0 from [6:0] to [7:0] |
| **Aug 20 2024** | Tri Vo | 0.8 | TX: () Update FIFO 5GHz: TxDat[3:0] to TxDat[7:0] RdPtr[1:0] to RdPtr[7:0] Update figure 3-3, 3-4 Update description of pin TxResEn TX_CAL: remove RdPtrInitOut () |
| **Jul 31 2024** | Chinh Ngo | 0.7 | Table 3-1 : Remove pins TxClk0FineTune[2:0] , TxClk90FineTune[2:0, TxClk180FineTune[2:0], TxClk270FineTune[2:0] Update TX block diagram – Remove above pins Update TX CAL pin list - Remove pins TxClk0FineTune[2:0] , TxClk180FineTune[2:0] Update TX CAL block diagram – Remove above pins Remove VDDC |
| **Jul 23 2024** | Tri Vo | 0.61 | TX_CAL: add pin RdClkOut |
| **Jul 01 2024** | Chinh Ngo | 0.6 | Add section 3.4.6 : First in First Out (FIFO) Add section 3.4.7 : Feed forward equalizer (FFE) setting – Guideline and setting code for TxFfeGain[3:0] Add pin TxResEn : No effect to function and use to Enable/Disable resistor feedback in TX design. Add notes in section 3.4.5 : Clock calibration – Need to disable FFE by configure TxFfeGain[3:0] = 4’b0000 Update clock calibration DCA section 3.4.5.2 according to Jira Update section 3.4.5.4 Phase correction sub-routine – Skip final code to overcome the non-monotonic Add table 3.4 : Configuration of calibration code with/without Flyover mode ( |
| **May 08 2024** | Tri Vo | 0.5 | dwc_ucie2phy_txsb/dwc_ucie2phy_tximp Change calibration code from 7 to 6 bits TxDeskew[4:0] to TxDeskew[3:0] dwc_ucie2phy_tx_cal: Remove pin: TxDcaCoarseClk90[4:0] TxDcaFineClk90[3:0] TxDeskewClk90[6:0] TxClk90FineTune[2:0] TxClk270FineTune[2:0] Add pins for Scan mode TxSe[1:0] TxCg TxSi[1:0] TxSo[1:0] Change pin CalOut[3:0] to CalOut |
| **Apr 19 2024** | Tri Vo | 0.4 | Add pin VDDC: dedicated power supply for clock path Increase bus width of TxClk*FineTune for 2 to 3 Remove pin TxDeskew[4:0] Change pin TxDesGain[3:0] to TxFfeGain[3:0] Add quadrature clock correction. New pins: TxDcaCoarseClk0[4:0] TxDcaFineClk0[3:0] TxDcaCoarseClk90[4:0] TxDcaFineClk90[3:0] TxDeskewClk0[6:0] TxDeskewClk90[6:0] TxDcdMode[1:0] TxDcdOffset[5:0] TxDcdClkSample TxDcdOut Add cell dwc_ucie2phy_tx_cal |
| **Mar 29 2024** | Chinh Ngo | 0.3 | dwc_ucie2phy_tx Add FIFO with scan chain to block diagram. Add FIFO pin WrPtr[1:0], WrPtrInit, RdPtr[1:0], RdPtrInit. Add scan pin : TxSe[1:0] , TxSi[1:0] , TxCg , TxSo[1:0]. Remove TxPreGain[3:0]. Add pin PhyClk for FIFO operating. Add pin TxResetn[1] to reset Flip Flops work at TxClk signal. dwc_ucie2phy_tx_rep Change TxSerOut to TxRepOut |
| **Jan 22 2024** | Tri Vo | 0.2 | All cell: Change cell name prefix from uciephy to ucie2phy Increase deskew bit from 4 to 5 dwc_ucie2phy_tx Add pin TxBias and TxVref for built-in differential receiver dwc_ucie2phy_tx Remove pin TxClk*BufOut |
| **Sep 27 2023** | Tri Vo | 0.1 | Initial version |

# Introduction

The UCIE interface I/O Buffers are high speed I/O buffers designed for die-to-die interface over short communication channels.

These buffers are designed to meet the requirements of different communication channels over an interposer to drive data between dices that are near the control device.

The data book includes:

- dwc_ucie2phy_tx8b: 40Gbps/20GHz Singled Ended Data Transmitter with 8-bit input data
- dwc_ucie2phy_tx16b: 40Gbps/20GHz Singled Ended Data Transmitter with 16-bit input data
- dwc_ucie2phy_txsb: 1Gbps/1Ghz Singled Ended Sideband Transmitter
- dwc_ucie2phy_tximp: a simple version of dwc_ucie2phy_txsb, used for the output impedance calibration and drive the digital test pad. This is for BGA C4 signal LUP purpose
# Overview

## Input Specification

### Common Input Specification

Table 21 Common Input Spec

| Parameters | Specification | Note |
| --- | --- | --- |
| UCIe Standard | 2.0 |  |
| Max Speed | Mainbands, TX 32Gbps/16Ghz Sideband, TXSB 1Gbps/1GHz |  |
| Design features | Calibrated Output Impedance Driver strength: 22/25/30/40 Ohm |  |
| VDD | 0.75V +/-10% |  |
| VCCIO | Multiple IO supply | 0.75V VCCIO require constraint: VCCIO <=VDD+25mV |
| VCCAON | 0.75V+/-10% |  |
| Mainband TX input clock | 10GHz |  |
| ESD Spec | 100mA: UCIe-A 300mA: UCIe-S |  |

### Mainband Transmitters (tx)

#### Output Impedance

Table 22 UCIe-A Single Ended output pad's 25Ohm Output Impedance

| **Symbol** | **Parameter** | **PAD Voltage (V)** | **M****in** | **Typ** | **M****ax** | **Unit** |
| --- | --- | --- | --- | --- | --- | --- |
| Rout_PD | Pull down impedance | 0.5* VCCIO | 22 | 25.00 | 28 | Ohm |
| Rout_PU | Pull up impedance | 0.5* VCCIO | 22 | 25.00 | 28 |  |

Table 23 UCIe-S Single-ended output pad’s 30Ohm output impedance

| **Symbol** | **Parameter** | **PAD Voltage (V)** | **M****in** | **Typ** | **M****ax** | **Unit** |
| --- | --- | --- | --- | --- | --- | --- |
| Rout_PD | Pull down impedance | 0.5* VCCIO | 27 | 30.00 | 33 | Ohm |
| Rout_PU | Pull up impedance | 0.5* VCCIO | 27 | 30.00 | 33 |  |

#### Pull Up and Pull Down Impedance mismatch with calibration

Pull Up and Pull Down Impedance mismatch is measured by the absolute difference between Pull Down Impedance and Pull Up Impedance at the same condition of temperature and voltage.

Table 24 Single-ended output pad’s pull up and pull down impedance mismatch with calibration

| **Symbol** | **Output ****Impedance**** Setting** | **M****ax** | **PAD Voltage (V)** | **Unit** |
| --- | --- | --- | --- | --- |
| Rout_MM | 25.00 | 2.50 | 0.5*VCCIO | Ohm |
| Rout_MM | 30.00 | 3.00 | 0.5*VCCIO | Ohm |

### Sideband transmitter (txsb)

Table 25 Sideband Input Specification

| **Description** | **Parameter** | **Condition** | **Min** | **Typ** | **Max** | **Unit** |
| --- | --- | --- | --- | --- | --- | --- |
| Supply voltage (VCCAON) |  |  | 0.65 |  |  | V |
| TX Swing | Vos |  | 0.8*VCCAON |  |  | V |
| Output high voltage | VOH |  | 0.9*VCCAON |  |  | V |
| Output low voltage | VOL |  |  |  | 0.1*VCCAON | V |

### TX replica for BGA Output driver (tximp)

## Performance Specification

# Mainband Transmitter

## FEATURES

- Single Ended output
- Quarter-rate architecture
- Built-in quadrature clock correction
- Feed-forward equalizer to compensate for channel loss
- Maximum input clock frequency: 10.0GHz
- Maximum output data rate: 40.0Gbps
- Configurable to support haft-rate or quarter-rate forwarded clock
- Programmable Output Impedance: 25/30 Ohm
- Driver currents are calibrated by 25 Ohm external resistor Calibration
- Synchronous input data and TX enable signal
- Asynchronous mode (flyover mode for boundary scan)
- Internal loopback mode: pre-loopback and post-loopback
- Built-in differential receiver for post-loopback
- No IO retention supported
- ESD: 0.1A CDM for UCIe-A, 0.3A CDM for UCIe-S
The cell list is shown in Table 31. They have the same function and pin interface.

Table 31 Mainband TX cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_tx16b_a_ns/ew | TX with 16-bit data input. Support UCIe-A, NS/EW PHY orientation |
| **2** | dwc_ucie2phy_tx16b_s_ns/ew | TX with 16-bit data input. Support UCIe-S, NS/EW PHY orientation |

## PINS DESCRIPTION

### TX with 16-bit input data

Table 32 Pin description of TX width 16-bit input data

| **Pin** | **Direction** | **Type** | **Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | - | Core power supply |
| VCCAON | Input | Power | VCCAON | - | 0.75V IO supply |
| VCCIO | Input | Power | VCCIO | - | UCIe IO supply for final driver |
| VSS | Input | Ground | VSS | - | Common ground |
| soft_VDD | Output |  | VDD | - | Soft VDD, used for pin tie-off |
| soft_VIO | Output |  | VCCIO | - | Soft VIO, used for pin tie-off |
| soft_VSS | Output |  | VDD | - | Soft VSS, used for pin tie-off |
| PAD_VIO | Output | Digital | VCCIO | - | Output PAD |
| TxPadRep | Output | Digital | VDD | - | Replica serializer output – Use for clock calibration |
| PhyClk | Input | Clock | VDD | - | High speed PHY clock. The frequency is 1/4 of TxClk* |
| TxClk0 | Input | Clock | VDD | - | High speed input clock with phase 0 degree Sampling TxDat[3:0] and TxEn |
| TxClk90 | Input | Clock | VDD | - | High speed input clock with phase 90 degree |
| TxResetn[1:0] | Input | Digital | VDD | - | Asynchronous reset, active low TxResetn[0]: Reset for Flip Flop works with PhyClk domain. TxResetn[1]: Reset for Flip Flop works with TxClk domain. |
| TxEn | Input | Digital | VDD | PhyClk | Synchronous Tx enable |
| TxDat[15:0] | Input | Digital | VDD | PhyClk | Synchronous Tx data input of FIFO |
| TxDatWrEn[2:0] | Input | Digital | VDD | PhyClk | FIFO write pointer |
| TxForceAsync | Input | Digital | VDD | Async | Force asynchronous mode |
| TxEnAsync | Input | Digital | VDD | Async | Asynchronous Tx enable |
| TxDatAsync | Input | Digital | VDD | Async | Asynchronous Tx data input |
| LbEn | Input | Digital | VDD | Async | Enable loopback function |
| LbMode | Input | Digital | VDD | Async | Select loopback mode: 0: pre-loopback 1: post-loopback |
| LbDatInSel | Input | Digital | VDD | Async | Enable when independently test TX IO or loopback sampler training 0: Compare data between 2 adjacent TX 1: Compare data with fixed data patterns |
| LbDatIn[3:0] | Input | Digital | VDD | - | Expected loopback data – coming from adjacent TX IO. If LbDatIn == LbDatOut Loopback passed. |
| LbFxdDatIn[3:0] | Input | Digital | VDD | Async | Used for fixed data patterns during loopback sampler training or when independently test the transmit IO |
| LbDeskew[2:0] | Input | Digital | VDD | Async | Used to deskew loopback clock |
| LbDout | Output | Digital | VDD |  | Full speed loopback data out |
| LbDatOut[3:0] | Output | Digital | VDD | TxClk0 | Loopback data out after de-serializer, data rate = LbDout data rate / 4 |
| TxDcdIn | Input | Digital | VDD | TxDcdClkSample | Duty cycle detector output 0: duty cycle < 50% 1: duty cycle > 50% |
| TxStatus | Output | Digital | VDD | Async | In clock calibration phase, it is output of duty cycle detector In loopback mode, it is output of checker |
| TxCalP[5:0] | Input | Digital | VDD | Async | 6 bits binary calibration code for pull up impedance |
| TxCalN[5:0] | Input | Digital | VDD | Async | 6 bits binary calibration code for pull down impedance |
| PwrOk_VAON | Input | Digital | VCCAON | Async | Power OK signal |
| TxDcaCoarseClk0[4:0] | Input | Digital | VDD | Async | Coarse Control Digital Word for coarse duty cycle adjust – Clock 0. Default 0 for 50% input duty cycle |
| TxDcaFineClk0[3:0] | Input | Digital | VDD | Async | Fine Control Digital Word for fine duty cycle adjust – Clock 0. Default 0 for 50%input duty Cycle |
| TxDcaCoarseClk90[4:0] | Input | Digital | VDD | Async | Coarse Control Digital Word for coarse duty cycle adjust – Clock 0. Default 90 for 50% input duty cycle |
| TxDcaFineClk90[3:0] | Input | Digital | VDD | Async | Fine Control Digital Word for fine duty cycle adjust – Clock 0. Default 90 for 50%input duty Cycle |
| TxDeskewClk0[7:0] | Input | Digital | VDD | Async | Lane-to-lane de-skew and phase adjustment for TxClk0 |
| TxDeskewClk90[7:0] | Input | Digital | VDD | Async | Lane-to-lane de-skew and phase adjustment for TxClk90 |
| TxClkCalEn | Input | Digital | VDD | Async | Clock calibration enable. The replica backend is enabled when assert TxClkCalEn |
| TxEqGain[3:0] | Input | Digital | VDD | Async | Select de-emphasis gain for channel equalizer. Can share for all TXs 4’b0000: disable FFE 4’b1111: max gain |
| TxResEn | Input | Digital | VDD | Async | Use to Enable/Disable Resistor feedback in TX design, no effect to the functional 1’b1: Optimal performance 1’b0: Optimal power |
| TxResPuSel[1:0] | Input | Digital | VDD | Async | Applicable for TX compatible. Refer to 3.2.2 |
| TxResPdSel[1:0] | Input | Digital | VDD | Async | Applicable for TX compatible. Refer to 3.2.2 |
| TxSe | Input | Digital | VDD | Async | Boundary scan shift enable, active high |
| TxSi | Input | Digital | VDD | PhyClk/ TxClk0 | Boundary scan shift input |
| TxCg | Input | Digital | VDD | Async | Boundary scan shift clock gater in FIFO |
| TxSo | Output | Digital | VDD | PhyClk/ TxClk0 | Boundary scan shift output |
| Reserved[3:0] | Input | - | VDD | - | Spare bits, floating |

### TX UCIe compatible

TX UCIe compatible is specially designed for low power requirement. The electrical specifications are not fully compliant with UCIe standard specification.

The pin list is unchanged, but the ResPu/PdSel pins and FFE gain selection are used to control the passive CTLE (channel equalization).

Table 33 TX compatible pin description

| **Pin** | **Direction** | **Type** | **Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| TxResPuSel[1:0] | Input | Digital | VDD | Async | Control pull-up termination resistor |
| TxResPdSel[1:0] | Input | Digital | VDD | Async | Control pull-down termination resistor |
| TxEqGain[1:0] | Input | Digital | VDD | Async | Select CTLE resistor value |
| TxEqGain[3:2] | Input | Digital | VDD | Async | Select CTLE capacitor value |

## FUNCTIONAL BLOCK DIAGRAM

Figure 31 Block diagram of Mainband TX – compliance version

Figure 32 Block diagram of Mainband TX – compatible version

*Note: N is input data bus width (8 or 16 bit)*

The frontend receives the data, clock, and control signal from digital side. The 2-phase clock is converted to 4-phase clock. Data from digital side is captured and then feed into 1-tap generator. The serializer converts 4 data inputs (up to 10Gbps) into one bit stream (up to 40Gbps). Clock de-skew is implemented to compensate for data lanes skew.

The predriver gets the data from frontend and pullup/pulldown calibration control as input and it generates the final backend driver segment control. The predriver logic is operating on VDD domain.

The backend contains 16 data slices to support FFE coefficient trimming. They can be turned on/off in opposite direction to create multiple output PAD level (des-emphasis). Each data slice contains pullup/pulldown legs to support impedance trimming. All 16 data slices operate on VCCIO domain.

The differential receiver is a very simple receiver for post-loopback purpose. It receives the data from pad, convert data to VDD domain and send to LbDout.

## OPERATION

### CLOCK PHASE GENERATOR

The front-end block has built in phase generator. This block will convert two-phase input clock into 4-phase clock with 90-degree phase difference.

Figure 33 Clock phase generator

### FIFO

Figure 34 Block diagram of FIFO with 16-bit input data

** **

** **

Figure 35 FIFO operation waveform

### TAP GENERATION AND SERIALIZER

The overall block diagram of 1-tap generation is shown in Figure 36. The re-timer flops capture the input data from digital side at every CK0 rising edge. The D-latches are used to generate appropriate delay shift for serializer block and generate complimentary data stream that is offset by 1 UI (post tap) to enable the FFE.

The critical timing path is from flop to latch and latch to latch. space from flop-2-latch or latch-2-latch is at least 2UI to ensure timing.

There are two serializer blocks to generate the bit stream for main tap and for post tap. The operation waveform is shown in Figure 37.

Figure 36 Block diagram of 1-tap generation

Figure 37 Operation waveform of 1-tap generation and serializer

### MISSION MODE

#### Synchronous mode

The data inputs TxDat[N-1:0] and TxEn get captured on the positive edge of PhyClk. There is an internal FIFO for buffering the data from PhyClk domain to TX clock domain. The data output bit rate at PAD_VIO is 4x the TX input clock frequency.

The dwc_ucie2phy_tx block is a non-inverting driver.

Table 34 Synchronous mode decode table

| Input | Output |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| PwrOk_VAON | TxForceAsync | TxEn | TxDat [N-1:0] | TxClk0 | TxClk90 | PAD_VIO |
| 0 | x | x | x | x | x | High-Z output |
| 1 | 0 | 0 | x | x | x | High-Z output |
| 1 | 0 | 1 | 0/1 | 0/1 | 0/1 | TxDat[N-1:0] |

Note: x = don’t care

Operation waveform:

Figure 38 Synchronous mission mode operation waveform

#### Asynchronous mode

In this mode, the state of PAD_VIO is controlled by TxEnAsync and TxDatAsync. FFE feature is disabled. The output impedance is fixed as Table 36.

The maximum data rate is 400Mbps.

Table 35 Asynchronous mode decode table

| Input | Output |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PwrOk_VAON | TxForceAsync | TxEnAsync | TxDatAsync | TxEn | TxDat [N-1:0] | TxClk0 | TxClk90 | PAD_VIO |
| 0 | x | x | x | x | x | x | x | High-Z output |
| 1 | 1 | 0 | x | x | x | x | x | High-Z output |
| 1 | 1 | 1 | 0 | x | x | x | x | 0 |
| 1 | 1 | 1 | 1 | x | x | x | x | 1 |

Note: x = don’t care

Figure 39 Asynchronous mission mode operation waveform

Table 36 Calibration codes effect in Pre-driver

| TxForceAsync | TxEnAsync | TxEn | PDEN_VD[5:0] | PUEN_VD [5:0] | PUEN_VDP[5:0] |
| --- | --- | --- | --- | --- | --- |
| 0 | x | 0 | 6’b0 | 6’b0 | 6’b1 |
| 0 | x | 1 | TxCalN[5:0] | TxCalP[5:0] | ! (TxCalP[5:0]) |
| 1 | 0 | x | 6’b0 | 6’b0 | 6’b1 |
| 1 | 1 | x | 6’b10000 | 6’b100000 | 6’011111 |

#### Clock mode

User can configure the TX to support haft-rate forwarded clock or quarter-rate forwarded clock by program TxDat[N-1:0].

- Half-rate forwarded clock: the output PAD frequency is 2x TxClk* frequency.
- CK_T: TxDat[N-1:0] = N’b10101010…0101
- CK_C: TxDat[N-1:0] = N’b01010101…1010
- Quadrature-rate forwarded clock: the output PAD frequency is the same as TxClk* frequency.
- CK_T: TxDat[N-1:0] = N’b00110011…0011
- CK_C: TxDat[N-1:0] = N’b01100110…0110
**Notes** : When clock mode is enabled, TxEqGain[3:0] must be set 4’b0000

### LOOPBACK MODE

#### Loopback setting

Table 37 Loopback decode table

| TxEn | LbEn | LbMode | Mode |
| --- | --- | --- | --- |
| 0 | 1 | 0 | Pre-loopback |
| 1 | 1 | 1 | Post-loopback |

#### Loopback training

Refer to section 5.7.2.7 Main band Transmit Near-Side Loopback Training

//depot/products/ucie/common/dev_2.0/arch/doc/dwc_uciephy_architecture_specification.pdf

### CLOCK CALIBRATION

Duty cycle and phase error significantly affect to the TX deterministic jitter, and they need to be corrected before data transaction. The concept of clock calibration is that the input clocks are converted to a signal clock after the serializer and then monitoring the duty cycle of the output clock to adjust the duty cycle and phase of the input clocks.

The duty cycle detector (DCD) is responsible for monitoring the duty cycle. It converts the clock to DC level and compare to a referent voltage. TxDcdOut goes high when duty cycle is larger than 50% and goes low when duty cycle is less than 50%.

There are two DCAs (named TxDCA0 and TxDCA90) and two DLL-based BDLs (named BDL0 and BDL90) for TxClk0 and TxClk90 respectively.

The calibration process involves 3 steps: duty cycle correction (dcc) for TxClk0, duty cycle correction for TxClk90 and phase correction between TxClk0 and TxClk90. Each step requires several specific data input patterns as described in Table 38. To find the optimal DCA code for both data and clock pattern in terms of jitter as well as eliminate the intrinsic error of DCD cell, the input patterns to TX are varied among 6 patterns to mimic the differential sensing methodology. So each calibration step needs two input patterns: odd and even. In “even” pattern, the digital Finite State Machines (FSM) must invert the value of TxDcdOut before using its value.

**Notes****: ****Before clock calibration,**** ****the FFE must be disabled (****TxEqGain****[3:0] = 4’b000****0****)**** and**** the comparator offset**** calibration**** need to**** be**** ****completed**** first****.**

Table 38 Input pattern for clock calibration

| # | TxDat[N-1:0] | Description |
| --- | --- | --- |
| 1 | P1 | TxClk0 dcc (odd) |
| 2 | P2 | TxClk0 dcc (even), FSM must invert value of TxDcdOut |
| 3 | P3 | TxClk90 dcc (odd) |
| 4 | P4 | TxClk90 dcc (even) , FSM must invert value of TxDcdOut |
| 5 | P5 | Phase correction (odd) |
| 6 | P6 | Phase correction (even) , FSM must invert value of TxDcdOut |

Table 39 Programmable data pattern for specific project

| Project | P1 | P2 | P3 | P4 | P5 | P6 |
| --- | --- | --- | --- | --- | --- | --- |
| H200 (32G, ucie-like) | 0011_0011_ 0011_0011 | 1100_1100_ 1100_1100 | 0110_0110_ 0110_0110 | 1001_1001_ 1001_1001 | 0101_0101_ 0101_0101 | 1010_1010_ 1010_1010 |
| H201 H202 H210 (Compatible – Serialize sense) | 1001_1001_ 1001_1001 | 0110_0110_ 0110_0110 | 0011_0011_ 0011_0011 | 1100_1100_ 1100_1100 | 1010_1010_ 1010_1010 | 0101_0101_ 0101_0101 |
| H213 (compliance – Post-tap serialize sense) | 1100_1100_ 1100_1100 | 0011_0011_ 0011_0011 | 1001_1001_ 1001_1001 | 0110_0110_ 0110_0110 | 0101_0101_ 0101_0101 | 1010_1010_ 1010_1010 |

#### Comparator offset calibration

1. Enable Comparator by setting csrPclkDCDEn = 1.

2. Put DCD circuit into offset mode, csrDCDOffsetMode = 1.

3. Wait DCDOffsetSettleInitial

4. Set csrDCDOffset to {min value} (-63)

5. Foreach csrDCDOffset, wait DCDOffsetSampleTime, then sample DCDOut by 1 cycle of SampleClk, wait for 2 DFICLK cycles.

6. If DCDOut == 1, stop; else increment csrDCDOffset and Goto step 5

7. Record csrDCDOffset as MinMaxOffset

8. Set csrDCDOffset to {max value} (+63)

9. Foreach csrDCDOffset, wait DCDOffsetSampleTime, then sample DCDOut by 1 cycle of SampleClk, wait for 2 DFICLK cycles

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
- default and reset value are: 7’b000000 this is the state of no offset.
- min value: -63 (6’b1111111)
- max value: +63 (6’b0111111)
#### Clock calibration process

User must assert TxClkCalEn and deassert TxEn during clock calibration process. After calibration process, TxClkCalEn can be kept asserting if power consumption is not a concern. It will help to minimize the aging effect.

Table 310 Truth table of TxClkCalEn

| Input | Output |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TxForceAsync | TxEn | TxClkCalEn | TxDat [N-1:0] | TxClk0 | TxClk90 | TxPadRep | PAD_VIO |
| 0 | 0 | 0 | x | x | x | 0 | High-Z |
| 0 | 0 | 1 | 0/1 | 0/1 | 0/1 | TxDat[N-1:0] | High-Z |

Figure 310 Clock calibration process

Note:

- BdlClk0 and BdlClk90 are decimal number and represent for TxDeskewClk0[7:0] and TxDeskewClk90[7:0] respectively. Decoder is defined in Table 311.
- Refer to Table 38 for data pattern P1 to P4
#### Duty cycle adjustment Sub-routine

Duty cycle adjustment (DCA) is one sub-routine involved in the clock calibration process and is described as below flow chart.

Figure 311 Duty cycle adjustment flow chart

**Notes** :

“Settling time” is defined in the specification of DCD cell.

#### Phase correction sub-routine

Phase correction is one sub-routine involved in the clock calibration process and is described as below flow chart.

Figure 312 Phase correction flow chart

**Notes** :

- “Settling time” is defined in the specification of DCD cell.
- BdlClk0 and BdlClk90 are decimal number and represent for TxDeskewClk0[7:0] and TxDeskewClk90[7:0] respectively. Decoder is defined in Table 311.
#### Majority Vote

Please see more details at section 3.10 “zcal_vote Design Description” of //depot/products/ucie/common/dev_2.0_2408TC/design/doc/softip/softip_zcal_design_specification/softip_zcal_design_specification.docx

#### Data pattern (p1/p2/p3/p4) for clock calibration

#### TxDeskewClk* glitchless control sequence.

The TX front-end includes 2 based-BDL blocks for phase correction and lane2lane de-skew purpose. The based-BDL is designed to support the glitch-less feature. The design uses 8bit TxDeskewClk*[7:0] setting to provide 96 phases shifting. Below is the glitch-less sequence for BDL setting code update.

There is “1ns” timing constraint between TxDeskewClk*[5:0] update and TxDeskewClk*[7:6] update for updating at code 32,64. Sequence:

- Count up:
- Update TxDeskewClk*[5:0] by increasing BDL delay phase from 31 to 32 or BDL delay phase from 63 to 64
- Wait t_bdl_settling
- Increase TxDeskewClk*[6] or TxDeskewClk*[7]
- Count down:
- Update TxDeskewClk*[5:0] by decreasing BDL delay phase from 33 to 32 or BDL delay phase from 65 to 64
- Wait t_bdl_settling
- Decrease TxDeskewClk*[6] or TxDeskewClk*[7]
Figure 313 : Glitchless phase update for BDL_crs_even(TxDeskewClk*[7:6])

Figure 314 : Glitchless phase update for BDL_crs_odd(TxDeskewClk*[7:6])

Table 311 BDL decoder

| **BDL delay phase** | **TxDeskewClk<7:6>** **(crs_odd,crs_even)** | **TxDeskewClk<5:0>** **(fine_pi[5:2],fine_sc[1:0])** | **BDL delay phase** | **TxDeskewClk<7:6>** **(crs_odd,crs_even)** | **TxDeskewClk<5:0>** **(fine_pi[5:2],fine_sc[1:0])** |
| --- | --- | --- | --- | --- | --- |
| 0 | 00 | 000000 | 48 | 01 | 110000 |
| 1 | 00 | 000001 | 49 | 01 | 110001 |
| 2 | 00 | 000010 | 50 | 01 | 110010 |
| 3 | 00 | 000011 | 51 | 01 | 110011 |
| 4 | 00 | 000100 | 52 | 01 | 110100 |
| 5 | 00 | 000101 | 53 | 01 | 110101 |
| 6 | 00 | 000110 | 54 | 01 | 110110 |
| 7 | 00 | 000111 | 55 | 01 | 110111 |
| 8 | 00 | 001000 | 56 | 01 | 111000 |
| 9 | 00 | 001001 | 57 | 01 | 111001 |
| 10 | 00 | 001010 | 58 | 01 | 111010 |
| 11 | 00 | 001011 | 59 | 01 | 111011 |
| 12 | 00 | 001100 | 60 | 01 | 111100 |
| 13 | 00 | 001101 | 61 | 01 | 111101 |
| 14 | 00 | 001110 | 62 | 01 | 111110 |
| 15 | 00 | 001111 | 63 | 01 | 111111 |
| 16 | 00 | 010000 | 64 | 11 | 000000 |
| 17 | 00 | 010001 | 65 | 11 | 000001 |
| 18 | 00 | 010010 | 66 | 11 | 000010 |
| 19 | 00 | 010011 | 67 | 11 | 000011 |
| 20 | 00 | 010100 | 68 | 11 | 000100 |
| 21 | 00 | 010101 | 69 | 11 | 000101 |
| 22 | 00 | 010110 | 70 | 11 | 000110 |
| 23 | 00 | 010111 | 71 | 11 | 000111 |
| 24 | 00 | 011000 | 72 | 11 | 001000 |
| 25 | 00 | 011001 | 73 | 11 | 001001 |
| 26 | 00 | 011010 | 74 | 11 | 001010 |
| 27 | 00 | 011011 | 75 | 11 | 001011 |
| 28 | 00 | 011100 | 76 | 11 | 001100 |
| 29 | 00 | 011101 | 77 | 11 | 001101 |
| 30 | 00 | 011110 | 78 | 11 | 001110 |
| 31 | 00 | 011111 | 79 | 11 | 001111 |
| 32 | 01 | 100000 | 80 | 11 | 010000 |
| 33 | 01 | 100001 | 81 | 11 | 010001 |
| 34 | 01 | 100010 | 82 | 11 | 010010 |
| 35 | 01 | 100011 | 83 | 11 | 010011 |
| 36 | 01 | 100100 | 84 | 11 | 010100 |
| 37 | 01 | 100101 | 85 | 11 | 010101 |
| 38 | 01 | 100110 | 86 | 11 | 010110 |
| 39 | 01 | 100111 | 87 | 11 | 010111 |
| 40 | 01 | 101000 | 88 | 11 | 011000 |
| 41 | 01 | 101001 | 89 | 11 | 011001 |
| 42 | 01 | 101010 | 90 | 11 | 011010 |
| 43 | 01 | 101011 | 91 | 11 | 011011 |
| 44 | 01 | 101100 | 92 | 11 | 011100 |
| 45 | 01 | 101101 | 93 | 11 | 011101 |
| 46 | 01 | 101110 | 94 | 11 | 011110 |
| 47 | 01 | 101111 | 95 | 11 | 011111 |

#### Recommended Connection with DCD cell

Figure 315 Recommended connection between TX and DCD. (a) in a pair, (b) stand alone

### LANE TO LANE DESKEW

Refer to 5.7.2.2 Transmit Data Bit Deskew Search Algorithm. The TxDeskewClk* have same increment and start from the value found in the clock calibration phase.

//depot/products/ucie/common/dev_2.0/arch/doc/dwc_uciephy_architecture_specification.pdf

### TXRESEN USAGE

AC couple and resistive feedback inverter are implemented in TX macro to enhance performance when the data rate is from or above 24Gbps. The pin TxResEn is used to enable or disable this option. General guideline:

- User is recommended to set it to 1 when data rate is from or above 24Gbps. Otherwise, set it to 0.
- When system is put into low power mode (i.e. idle, standby, LP2, power down…) which the input clock is static, user must set it to 0.
In async mode, AC couple and resistive feedback is disabled internally.

### FEED FORWARD EQUALIZER SETTING

At very high data rates, the signal quality is severely impacted by frequency dependent losses leading to a reduced eye opening, reduced signal-to-noise ratio and increased inter symbol interference (ISI). Advanced equalizations are widely used to overcome bandwidth limitations in high-speed transmitter. To increase the data rate beyond 24Gb/s, a feed-forward equalizer (FFE), is required to compensate for the channel loss and to enhance the data rate by mean of introducing distortion of the transmitted signal waveform, diminishing the ISI effects.

For data rate below 24Gbps (Clock frequency 6Ghz), user must disable FFE by configuring the FFE code to 3’b000.

FFE has 16 settings to cover the wide range of channel loss (from 0 to -8dB) and this range is dependent on the CMOS tech node, thus the FFE code with same gain is process dependent. For example, with -3db gain, N5 will choose TxEqGain[2:0] = 3’b101 and SF4 will choose TxEqGain[2:0] = 3’b101.

The FFE gain setting is dependent on channel loss and receiver’s capability. User can consider all conditions to select the optimal setting for performance and power consumption. For example, if channel lost is 8.2db and receiver has channel equalizer capacity, the FFE gain is around -5dB and RX will handle the remaining.

**Note: TxEqGain is defined by the target data****, even ****PHY operates at 4Gbps**** during the PHY initialization. This is to make sure RX VREF training works properly.**** **

| Technology | TxEqGain[2:0] Setting | Gain Compensation (dB) | Gain step (dB) (*) |
| --- | --- | --- | --- |
| **SF4 (H200)** | 3’b000 | TBU |  |
|  | 3’b001 |  |  |
|  | 3’b010 |  |  |
|  | 3’b011 |  |  |
|  | 3’b100 |  |  |
|  | 3’b101 |  |  |
|  | 3’b110 |  |  |
|  | 3’b111 |  |  |
| **TSMC N5 (H201)** | 3’b000 | TBU |  |
|  | 3’b001 |  |  |
|  | 3’b010 |  |  |
|  | 3’b011 |  |  |
|  | 3’b100 |  |  |
|  | 3’b101 |  |  |
|  | 3’b110 |  |  |
|  | 3’b111 |  |  |

### IDLE MODE

Figure 316 Idle mode configuration

| Clocking mode | Link termination | Operation | TxEn | TxClk* | TxDat* |
| --- | --- | --- | --- | --- | --- |
| Strobe mode | No | Data transmit | 1 | OFF | 0 or 1 |
|  | No | Clock transmit | 1 | OFF | 0 |
|  | Yes | Data transmit | 0 | OFF | 0 or 1 |
|  | Yes | Clock transmit | 1 | OFF | 0 |
| Continuous mode | No | Data transmit | 1 | ON | 0 or 1 |
|  | No | Clock transmit | 1 | ON | *Clock mode* |
|  | Yes | Data transmit | 0 | ON | 0 or 1 |
|  | Yes | Clock transmit | 1 | ON | *Clock mode* |

The clocking mode is defined by RX side of partner die.

### STANDBY MODE

Standby mode is defined when the input clocks is static 0 (clocks are gated), input data is static 0 or 1 and the driver is disable. IO setting:

- TxForceAsync = 0
- TxEn = 0
- TxResEn = 0
- TxEqGain = 0
### LP3 MODE

When PwrOk_VAON is asserted Low, the driver is in “VDD supply not ready mode”, PAD will be high Z output to avoid crowbar current

Table 312 LP3 mode

| **PwrOk_VAON** | **Result** |
| --- | --- |
| 1 | Normal operation depending on data and enables |
| 0 | High-Z output |

### DFT

Table 313 DFT condition

| Pin | Value |
| --- | --- |
| LbEn | 0 |

Table 314 DFT scan chain information of Mainband TX with 16-bit data width

| **No.** | **DFT input Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PhyClk | TxSi | TxSe | TxSo | rising | 49 | Refer block diagram for detail scan chain |

## IDDQ (leakage) Measurement

Table 315 IDDQ setting

| Pin | Value |
| --- | --- |
| TxForceAsync | 1 |
| TxEnAsync | 0 |

## Burn-in Test Recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run a combination of mission mode and loopback mode. Set TxDeskewClk0[6:0] and TxDeskewClk90[6:0] to max code.

User need to enable TxClkCalEn to exercise the replica driver.

## Anti-aging setting

To prevent Aging effect, the recommended setting is the same as burn-in test but with much lower frequency (i.e 25MHz).

## RTL AND TIMING REQUIREMENTS

TxBias and TxVref are analog signal generated from Bias cell. Don’t insert buffer.

Table 316 RTL Timing Requirement

| Parameter | Value | Description |
| --- | --- | --- |
| t_tx_enable | 1 PhyClk cycle | Need to assert TxEn first, at least 1 PhyClk cycle, then start data transaction. If user want to stop data transaction, user need to wait for data transaction completed and then deassert TxEn, at least 1 PhyClk cycle after data transaction. |
| t_tx_padrep_enable | - | No constrain |
| t_lb_enable | 1ns | Need to assert LbEn, LbMode first, at least 1 ns, then start data transaction |
| t_lbdatinsel | 1ns | Need to assert LbDatInSel first, at least 1ns , then start data transaction |
| t_bdl_settling | 1ns | Waiting time when change the BDL code before new data coming |
| t_pwrok_enable | 1ns | Waiting time from PwrOk_VAON assert to TX ready for data transaction |
| t_enasync_enable | 1ns | Waiting time from TxEnAsync assert to TX ready for data transaction |
| t_forceasync_enable | 1ns | Waiting time from TxForceAsync assert to TX ready for data transaction |
| t_DCDOffsetSettleInitial t_DCDMissionSettleInitial | 100ns | Settling Time |
| t_DCDOffsetSampleTime | 100ns | Comparator sample time in offset calibration mode |
| T_DCDMissionSampleTime | 100ns | Comparator sample time in mission mode |
| t_DCA_update_to_DCD | 150ns | Time requires from DCA update new code PclkDcaCoarse[4:0] and PclkDcaFine[3:0] until dcd_out of DCD valid for captured data. It’s included DCDSettleTime from DCD |
| t_DCA_update_to_PclkOut | 1ns | Time requires from DCA update new code PclkDcaCoarse[4:0] and PclkDcaFine[3:0] until output pin PclkOut of DCA valid. |
| t_PclkDcaMode_update_to_PclkOut | 1ns | Time requires from DCA change from mission mode to default mode via versa until output pin PclkOut of DCA valid. |

- Values are limited by DC voltage drop.
- TxClk to PAD_VIO propagation delay is measured from 50% of TxClk to 50% of PAD_VIO. Delay is measured with UCIe channel model
- Sim with zero PAD load.
## Delay Parameters

Table 317 Delay parameters of BDL for lane-2-lane de-skew

| Parameters | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- |
| t_bdl_zero_range | 40 |  | 80 | ps |
| t_bdl_deskew_range | 24 | 32 | 48 | ps |
| t_bdl_stepsize | 0.25 | 0.33 | 0.5 | ps |
| t_bdl_range_tolerance |  | 0.5 |  | t_bdl_stepsize |

Table 318 Delay parameters of BDL for loopback

| Parameters | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- |
| t_bdl_zero_range | 20 |  | 40 | ps |
| t_bdl_deskew_range |  | 15 | 25 | ps |
| t_bdl_stepsize | 1 | 2 | 3 | ps |
| t_bdl_range_tolerance |  | 0.5 |  | t_bdl_stepsize |

# FIFO Pointer calibration(dwc_ucie2phy_txcal)

## FEATURE

FIFO pointer calibration is used to determine the pointer separation between the write and read pointers of the PHY FIFOs. The default calibration gives about 1 PClk pointer separation. This separation can be increased up to a maximum value of 3 PClk separation. Bigger separation results in more margins between the writing and reading of FIFOs to absorb uncertainties due to VT drifts, but this also increases the latency of the data through the PHY.

With embedded phase detector, txcal can compare two input clocks and determine which one is earlier.

Figure 41 txcal cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_txcal16b_ns/ew | TX with 16-bit data input. Support both UCIe-A/S, NS/EW PHY orientation |

## PIN DESCRIPTION

| **Pin** | **Direction** | **Type** | **Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | - | Core power supply |
| VSS | Input | Ground | VSS | - | Common ground |
| PhyClk | Input | Clock | VDD | - | High speed input clock |
| TxClk0Dat | Input | Clock | VDD | - | High speed input clock with phase 0 degree. Connect to the nearest Data TX. |
| TxClk90Dat | Input | Clock | VDD | - | High speed input clock with phase 90 degree. Connect to the nearest Data TX. |
| TxClk0Ck | Input | Clock | VDD | - | High speed input clock with phase 0 degree. Connect to the nearest Clock TX |
| TxClk90Ck | Input | Clock | VDD | - | High speed input clock with phase 90 degree. Connect to the nearest Clock TX. |
| TxResetn[1:0] | Input | Digital | VDD | - | Asynchronous reset, active low TxResetn[0]: Use to reset for Flip Flop works with PhyClk domain. TxResetn[1]: Use to reset for Flip Flop works with TxClk domain. |
| TxResEn | Input | Digital | VDD | Async | Use to Enable/Disable Resistor feedback in TX design, no effect to the functional. It should have the same value as TX data |
| TxDcaCoarseClk0Dat[4:0] | Input | Digital | VDD | Async | Coarse Control Digital Word for coarse duty cycle adjust – Clock 0. Default 0 for 50% input duty cycle. Use the same code as the nearest Data TX |
| TxDcaFineClk0Dat[3:0] | Input | Digital | VDD | Async | Fine Control Digital Word for fine duty cycle adjust – Clock 0. Default 0 for 50%input duty Cycle Use the same code as the nearest Data TX |
| TxDeskewClk0Dat[7:0] | Input | Digital | VDD | Async | Lane-to-lane de-skew and phase adjustment for TxClk0. Default is 0. |
| TxDcaCoarseClk0Ck[4:0] | Input | Digital | VDD | Async | Coarse Control Digital Word for coarse duty cycle adjust – Clock 0. Default 0 for 50% input duty cycle. Use the same code as the nearest Clock TX. |
| TxDcaFineClk0Ck[3:0] | Input | Digital | VDD | Async | Fine Control Digital Word for fine duty cycle adjust – Clock 0. Default 0 for 50%input duty Cycle. Use the same code as the nearest Clock TX. |
| TxDeskewClk0Ck[7:0] | Input | Digital | VDD | Async | Lane-to-lane de-skew and phase adjustment for TxClk0. Default is 0. |
| TxDatWrEn[2:0] | Input | Digital | VDD | PhyClk | FIFO write pointer |
| TxDat | Input | Digital | VDD | PhyClk | FIFO write data |
| CalRstn | Input | Digital | VDD | PhyClk | FIFO calibration reset. Active low |
| CalOut | Output | Digital | VDD | TxClk0 | FIFO calibration output |
| TxEarly | Output | Digital | VDD | Async | Output of Phase detector, indicates clock of Data TX earlier than Clock TX |
| TxLate | Output | Digital | VDD | Async | Output of Phase detector, indicates clock of Data TX later than Clock TX |
| TxSe | Input | Digital | VDD | Async | Boundary scan shift enable, active high |
| TxCg | Input | Digital | VDD | Async | Boundary scan shift clock gater in FIFO |
| TxSi | Input | Digital | VDD | PhyClk | Boundary scan shift input |
| TxSo | Output | Digital | VDD | PhyClk | Boundary scan shift output |

## BLOCK DIAGRAM

Figure 42 Block diagram of txcal

Figure 43 Block diagram of Phase detector

## CLOCK PHASE COMPARISON

TXCAL receives two input clocks from two sources and there are two phase detectors used to detect which clock is early. The output of phase detectors is shown in Table 41

Table 41 Truth table of phase detector

| Clock phase relationship | TxEarly | TxLate |
| --- | --- | --- |
| **No clock cycle shifted** | 0 | 0 |
| **TxClk0Dat is early than TxClk0Ck** | 1 | 0 |
| **TxClk0Dat is later than TxClk0Ck** | 0 | 1 |

Figure 44 Operation waveform of clock phase detector

## DFT and RTL requirement

There is no special requirement for DFT, IDDQ measurement, burn-in test and anti-aging.

Table 42 DFT Scan chain in TXCAL with 16-bit data bus width

| **No.** | **DFT input Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PhyClk | TxSi | TxSe | TxSo | rising | 48 | Refer TXCAL block diagram for detail scan chain |

# Sideband Transmitter (dwc_ucie2phy_txsb)

## FEATURES

- Output Single Ended signaling
- Asynchronous mode: 1Gbps/1GHz
- Internal loopback mode: pre-loopback and post-loopback
- ESD: 40mA for UCIe-A, 0.3A for UCIe-S
Table 51 TXSB cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_txsb | Support both UCIe-A/S, and both NS/EW PHY orientation |

## PINS DESCRIPTION

Table 52 Single ended output buffer Pin Description

| **Pin** | **Type** | **Domain** | **Description** |
| --- | --- | --- | --- |
| VDD | Power | VDD | Core power supply |
| VCCAON | Power | VCCAON | 0.75V IO power supply |
| VSS | Ground | VSS | Common ground |
| PAD_VIO | Output | VCCAON | IO PAD |
| TxEn | Input | VDD | Tx enable |
| TxDat | Input | VDD | Tx data input |
| LbEn | Input | VDD | Enable loopback function |
| LbMode | Input | VDD | Available in Production, and from SF3* only Select loopback mode. 0: pre-loopback 1: post-loopback |
| LbDout | Output | VDD | Loopback data out |
| PwrOk_VAON | Input | VCCAON | Power OK signal |
| TxCalP[5:0] | Input | VDD | 6 bits binary calibration code for pull up impedance |
| TxCalN[5:0] | Input | VDD | 6 bits binary calibration code for pull down impedance |
| TxDeskew[3:0] | Input | VDD | Per bit deskew select 4'b0000: minimum delay 4'b1111: maximum delay |
| Reserved[3:0] | Input | VDD | Spare bit, floating |
| soft_VDD | Output | VDD | Soft VDD, used for pin tie-off |
| soft_VSS | Output | VDD | Soft VSS, used for pin tie-off |

## FUNCTIONAL BLOCK DIAGRAM

### BLOCK DIAGRAM

Basic architecture at a high level is shown Figure 51

Figure 51 Block diagram of dwc_ucie2phy_txsb

### CALIBRATION CODE SETTING

Pin TxCalP[5:0] and TxCalN[5:0] must be configured properly according to a specific usage.

Table 53 Calibration code setting for dwc_ucie2phy_txsb (TBD)

| **Usage** | **TxCalP****[5:0]** | **TxCalN****[5:0]** |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

Note:

(*) User should use soft_VDD and soft_VSS to configure code, no need to use the additional logic

## Operation modes

### MISSION MODE

dwc_ucie2phy_txsb can be used to transmit both data and clock. In clock mode, TxDat pattern is 101010…

Table 54 Mission mode decode table

| **Input** | **Output** |  |  |
| --- | --- | --- | --- |
| **PwrOk_VAON** | **TxEn** | **TxDat** | **PAD_VIO** |
| 0 | x | x | High-Z output |
| 1 | 0 | x | High-Z output |
| 1 | 1 | 0 | 0 |
| 1 | 1 | 1 | 1 |

- Note: x = don’t care
- Operation waveform:
Figure 52 Operation waveform in mission Data mode

Figure 53 Operation waveform in mission Clock mode

### LOOPBACK MODE

#### Pre-loopback mode

Table 55 Pre-loopback mode decode table

| **Input** | **Output** |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **PwrOk_VAON** | **TxEn** | **LbEn** | **LbMode** | **TxDat** | **LbDout** |
| x | x | 0 | x | x | 0 |
| x | x | 1 | 0 | 0 | 0 |
| x | x | 1 | 0 | 1 | 1 |

- Note: x = don’t care
- It is recommended to set TxEn to 0 in pre-loopback mode to reduce power noise
- Operation waveform:
Figure 54 Operation waveform in Pre loopback mode

#### Post-loopback mode

Table 56 Post-loopback mode decode table

| Input | Output |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| PwrOk_VAON | TxEn | LbEn | LbMode | TxDat | PAD_VIO | LbDout |
| 0 | x | x | x | x | High Z | 0 |
| 1 | 0 | 0 | x | x | High Z | 0 |
| 1 | 1 | 0 | x | 0/1 | 0/1 | 0 |
| 1 | 0 | 1 | 1 | x | High Z | 0 |
| 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Note: x = don’t care

Operation waveform:

Figure 55 Operation waveform in Post loopback mode

### IDLE MODE

Idle mode is defined when TxDat is statis (0 or 1), but the driver is still enabled (TxEn = 1’b1).

### STANDBY MODE

Standby mode is defined when TxDat is statis (0 or 1), but the driver is disabled (TxEn = 1’b0).

### LP3 MODE

When PwrOk_VAON is asserted Low, the driver is in “VDD supply not ready mode”, PAD is high Z

Table 57 VDD not ready mode decode table

| **PwrOk_VAON** | **Result** |
| --- | --- |
| 1 | Mission Mode |
| 0 | High-Z output |

### DFT

Table 58 TXSB DFT condition

| Pin | Value |
| --- | --- |
| TxEn | 0 |

## IDDQ (leakage) Measurement

Table 59 IDDQ setting

| Pin | Value |
| --- | --- |
| TxEn | 0 |

## Burn-in Test Recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run a combination of mission mode and loopback mode.

## RTL AND TIMING REQUIREMENTS

Table 510 RTL Timing Requirement

| Parameter | Value | Macro | Description |
| --- | --- | --- | --- |
| t_tx_enable | 250ps | txsb | Need to assert TxEn first, at least 1 cycle, then start data transaction. If user want to stop data transaction, user need to wait for data transaction completed and then deassert TxEn, at least 1 cycle after data transaction. |
| t_lb_enabling | 250ps | txsb | Need to assert LbEn, LbMode first, at least 1 cycle, then start data transaction |
| t_bdl_settling | 500ps | txsb | Waiting time when change the BDL code before new data coming |

# BGA Output driver (dwc_ucie2phy_tximp)

## FEATURES

This cell is a stripped-down version of dwc_ucie2phy_tx. The main purpose of this cell is for BGA signals including the output current calibration (ZQ) and driving the high-speed internal clock to off chip for observation (testout).

This cell is optimized to satisfy latch-up rule up to 0.825V I/O voltage.

All unnecessary parts of TX are removed, only pre-driver and main driver are kept. However, all interface pins are kept same.

The main feature:

- Output Single Ended
- Asynchronous mode: 8Gbps/8GHz @ 500fF load
Table 61 TXIMP cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_tximp_a_ns/ew | Support UCIe-A, NS/EW PHY orientation |
| **2** | dwc_ucie2phy_tximp_s_ns/ew | Support UCIe-S, NS/EW PHY orientation |

## PINS DESCRIPTION

Table 62: Single ended output buffer Pin Description

| **Pin** | **Type** | **Domain** | **Description** |
| --- | --- | --- | --- |
| VDD | Power | VDD | Core power supply |
| VCCAON | Power | VCCAON | 0.75V IO power supply |
| VCCIO | Power | VCCIO | Power supply for main driver |
| VSS | Ground | VSS | Common ground |
| PAD_VIO | Inout | VCCIO | IO PAD |
| TxEn | Input | VDD | Tx enable |
| TxDat | Input | VDD | Tx data input |
| PwrOk_VAON | Input | VCCAON | Power OK signal |
| TxCalP[5:0] | Input | VDD | 6 bits binary calibration code for pull up impedance |
| TxCalN[5:0] | Input | VDD | 6 bits binary calibration code for pull down impedance |
| Reserved[3:0] | Input | VDD | Spare bit, floating |
| soft_VDD | Output | VDD | Soft VDD, used for pin tie-off |
| soft_VSS | Output | VDD | Soft VSS, used for pin tie-off |

## FUNCTIONAL BLOCK DIAGRAM

### BLOCK DIAGRAM

Figure 61 Block diagram of dwc_ucie2phy_tximp

### CALIBRATION CODE SETTING

Pin TxCalP[5:0] and TxCalN[5:0] must be configured properly according to a specific usage. Refer to Table 63 for more detail

Table 63: Calibration code setting for dwc_ucie2phy_tximp

| **Usage** | **TxCalP****[5:0]** | **TxCalN****[5:0]** |
| --- | --- | --- |
| Replica dwc_ucie2phy_tx for the output impedance calibration (ZQ) | Programmable | Programmable |
| Testout | Programmable | Programmable |

Note:

(*) User should use soft_VDD and soft_VSS to configure code, no need to use the additional logic

## Operation modes

### MISSION MODE

Table 64: Mission mode decode table

| **Input** | **Output** |  |  |
| --- | --- | --- | --- |
| **PwrOk_VAON** | **TxEn** | **TxDat** | **PAD_VIO** |
| 0 | x | x | High-Z output |
| 1 | 0 | x | High-Z output |
| 1 | 1 | 0 | 0 |
| 1 | 1 | 1 | 1 |

- Note: x = 0/1
- Operation waveform:
### IDLE MODE

Idle mode is defined when TxDat is statis (0 or 1), but the driver is still enabled (TxEn = 1’b1).

### STANDBY MODE

Standby mode is defined when TxDat is statis (0 or 1), but the driver is disabled (TxEn = 1’b0).

### LP3 MODE

When PwrOk_VAON is asserted Low, the driver is in “VDD supply not ready mode”, PAD is high Z

Table 65: VDD not ready mode decode table

| **PwrOk_VAON** | **Result** |
| --- | --- |
| 1 | Mission Mode |
| 0 | High-Z output |

### DFT

Input condition:

Table 66: DFT input condition for dwc_ucie2phy_tximp cell

| Pin | Value |
| --- | --- |
| TxEn | 0 |

## RTL AND TIMING REQUIREMENTS

Table 67 RTL Timing Requirement

| Parameter | Value | Macro | Description |
| --- | --- | --- | --- |
| t_tx_enable | 250ps | tx | Need to assert TxEn first, at least 1 cycle, then start data transaction. If user want to stop data transaction, user need to wait for data transaction completed and then deassert TxEn, at least 1 cycle after data transaction. |

# Simulation Plans

## dwc_ucie2phy_tx

Table 71 TX Simulation Plan

| **No** | **Testbench** | **Description ** |
| --- | --- | --- |
| **1** | tx_frontend_tran_post.bbSim | Measure timing for Frontend block |
| **2** | tx_predriver_tran_post.bbSim | Measure timing, crowbar current and overlap for Pre-driver |
| **3** | tx_backend_pu_dc_post.bbSim | Measure CALN code |
| **4** | tx_backend_pd_dc_post.bbSim | Measure CALP code |
| **5** | tx_backend_pd_step_dc_post.bbSim | Confirm value at 10mA code and measure current value of 1 step |
| **6** | tx_backend_pu_step_dc_post.bbSim | Confirm value at 10mA code and measure current value of 1 step |
| **7** | tx_backend_pd_aging_she_post.bbSim | Measure CALN code for aging corner |
| **8** | tx_backend_pu_aging_she_post.bbSim | Measure CALP code for aging corner |
| **9** | tx_backend_padcap_tran_post.bbSim | Measure pad Cap (transient method) |
| **10** | tx_backend_padlkg_dc_post.bbSim | Measure pad leakage |
| **11** | tx_top_timing_tran_post.bbSim | Measure timing for fullpath in Synchronous mode, BDL code =0 |
| **12** | tx_top_timing_bdlmax_lb_post.bbSim | Measure timing with max setting BDL for fullpath in Synchronous mode, and measure loopback path |
| **13** | tx_top_timing_aging_she_post.bbSim | Measure timing for fullpath in Synchronous mode affect by aging |
| **14** | tx_top_timing_monte_post.bbSim | Measure timing for fullpath in Synchronous mode varied by MC |
| **15** | tx_top_power_avg_post.bbSim | Measure avarage power of TX |
| **16** | tx_top_power_leakage_post.bbSim | Measure leakage power of TX (all signals are 0) |
| **17** | tx_top_power_lp2_post.bbSim | Measure static power of TX (PwrOk is 1) |
| **18** | tx_top_power_lp3_post.bbSim |  |
| **19** | tx_top_power_idle_post.bbSim | Measure power when Txdat is off (clk is active) |
| **20** | tx_top_linkmargin_isi_post.bbSim | measure jitter at LM corner, BDL max code |
| **21** | tx_top_linkmargin_zq_mismatch_post.bbSim | ISI mismatch when apply ZQ code at LM corners |
| **22** | tx_top_linkmargin_irdrop_post.bbSim | Measure Irdrop |
| **23** | tx_top_linkmargin_loopback_post.bbSim |  |
| **24** | tx_top_linkmargin_sso_post.bbSim | Measure SSO jitter |
| **25** | tx_top_vccio_rc_post.bbSim | Measure Rdie-Cdie VCCIO |
| **26** | tx_top_vccaon_rc_post.bbSim | Measure Rdie-Cdie VCCAON |
| **27** | tx_top_Rdie_c_post.bbSim | Measure Rdie-Cdie VDD |
| **28** | tx_top_func_post.bbSim | Cross functional check spice vs verilog |
| **29** | tx_top_dcck_post.bbSim | Dynamic CCK |
| **30** | tx_top_emir.bbSim | EMIR check |

## dwc_ucie2phy_tx_rep

Table 72 TX_REP simulation plan

| **No** | **Testbench** | **Description ** |
| --- | --- | --- |
| **1** | tx_rep_top_timing_tran.bbSim | Testbench include: tx_rep, tx, dcdMeasure duty cycle, proparation delay, slew of TxClkPSenMeasure duty cycle error: - TxClkPSen vs tx_rep se2diff output- TxClkPsen vs real TX se2diff output- tx_rep se2diff output vs real TX se2diff output |
| **2** | tx_rep_top_timing_aging_she.bbSim | Reuse above tb, measure all parameter after 10yrs |
| **3** | tx_rep_top_timing_monte_sigamp_<pvt>.bbSim | Testbench include: tx_rep, dcdMeasure the error caused by the additional buffers |
| **4** | tx_rep_emir_she.bbSim | EMIR verification |

## dwc_ucie2phy_txsb

Table 73 TXSB Simulation plan

| **No ** | **Testbench Name ** | **Description ** |
| --- | --- | --- |
| 1** ** | txsb_timing_async_tran_post.bbSim** ** | Measure timing in Async mode** ** |
| 2** ** | txsb_timing_async_monte_post.bbSim** ** | Monte Carlo sim timing in Async mode** ** |
| 3** ** | txsb_pu_dc_post.bbSim** ** | Measure pull up current** ** |
| 4** ** | txsb_pd_dc_post.bbSim** ** | Measure pull down current** ** |
| 5** ** | txsb_power_async_post.bbSim** ** | Measure active power in Async mode** ** |
| 6** ** | txsb_power_leakage_post.bbSim** ** | Measure leakage current for VDD and VCCIO when all inputs are off** ** |
| 7** ** | txsb_power_static_async_post.bbSim** ** | Measure power when TxData is static at 0** ** |
| 8** ** | txsb_psj_post.bbSim** ** | Measure power noise jitter** ** |
| 9** ** | txsb_padcap_ac_post.bbSim** ** | Measure pad cap when TxEn=0: non-transmit mode** ** |
| 10** ** | txsb_padlkg_dc_post.bbSim** ** | Measure pad leakage when TxEn=0: non-transmit mode ** ** |
| 11** ** | txsb_aging_she_timing_async_post.bbSim** ** | Aging sim in Async mode** ** |
| 12** ** | txsb_dcck_ac_overshoot_post.bbSim** ** | cck dynamic when Input signals: toggle all input.** ** |
| 13** ** | txsb_dcck_dc_stress_post.bbSim** ** | cck dynamic when Input signals: no toggle, including clocks.** ** |
| 14** ** | txsb_dcck_rampower_pre.bbSim** ** | cck dynamic when Power rampup/down, Input signals: no toggle, including clocks** ** |
| 15** ** | txsb_emir_she_post.bbSim** ** | EMIR sim** ** |

## dwc_ucie2phy_tximp

TBU
