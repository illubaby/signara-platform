**DesignWareCore**** ****UCIE**** PHY**

Data book

UCIE PHY CMPANA

dwc__cmpana

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

**List ****o****f Figures**

**List ****o****f Tables**

Revision History

| Version | Date | Author | Change Description |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
| 0.1 | , 202 |  |  |
|  |  |  |  |

Reference Documents

# Introduction

The incorporates a compensation engine *ZCAL* in the MMCTRL to calibrate the output driver impedance and termination impedance to match a target value of resistances from an external resistor

- Cell name: dwc__cmpana
- Maximum operating frequency in calibration (for CMPANA block): 2GHz
- Operation modes:
- UCIe-A: Comparator offset Calibration, Driver Pull-up Calibration & Driver Pull-down Calibration

- UCIe-S: Comparator offset Calibration, Driver Pull-up Calibration & Driver Pull-down Calibration Receiver Termination Calibration

The goal of the compensation engine is as follows:

- To find the -bit wide pull-up driver compensation code that gives the target DC resistance at the target voltage.
- To find the -bit wide pull-down driver compensation code that gives the target DC resistance at the target voltage.
- To find the 6-bit wide ODT RX compensation code that gives the target DC resistance at the target voltage.
- Transmit these codes to the mission mode drivers with minimal/no glitching of normal driver operation
# Overview

## Input Specification

Table 2 Input Specification

| Parameters | Specification | Note |
| --- | --- | --- |
| UCIe Standard | 1.0 |  |
| Max Speed | 2GHz |  |
| External |  |  |
| Design features | Calibrate an output impedance by an external resistor,provide scale factors for other settings |  |
| VDD |  |  |
| VCCIO |  | 0.75V VCCIO require constraint: VCCIO <=VDD+25mV |
|  |  |  |
| ESD Spec | HBM: 2kV CDM: 6A |  |

## Recommended operation condition

Table 2 Recommended operation condition

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
| **VDD** | Core supply | 0.675 | 0.75 | 0.825 | V |
| **V****CCIO** | IO supply |  |  |  | V |
| **VSS** | round | 0 | 0 | 0 | V |
| **Tj** | Junction temperature | -40 | 25 | 125 | C |

2

|  |  |  |
| --- | --- | --- |
|  |  |  |

# Functional Outline

## Calibration scheme (ZCAL)

The compensation engine houses the following:

- replica tximp act as calibration instances
- The analog calibrator macro* **dwc_**_cmpana *to generate a programmable voltage reference, multiplexing calibration nodes and provide analog filtering
- The digital module *dwc_**_zcaldig *to execute the compensation state machine
The calibrated by pulling up/down against and comparing the resulting voltage against a voltage reference.

FSM inside *dwc_**_zcaldig* walks through the above calibration steps in sequence. Each step starts with a test value and progressively converges to the “matching” compensation code based on the decision from the comparator inside *dwc_**_cmpana* that is fed back into *dwc_**_zcaldig*. The entire compensation routine is re-executed periodically inside the PHY to track Voltage-Temperature variations.

The *dwc_**_cmpana* macro supports the calibration requirements of specs.

3

## Macro Architecture

3

## Pin list

Table 3 Pin Description

| **Pin Name** |  |  | **Power** **Domain** | **Clock** **Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| ZCalLoad |  |  | V | Async |  |
| ZCalLoad |  |  |  | Async |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
| ZCalAnaEn |  |  | VDD |  | Enable Comparator, Ibias and Senseamp |
| ZCalCompEn |  |  | VDD |  | Comparator offset Calibration |
| ZCalEn |  |  | VDD |  |  |
| ZCalEn |  |  | VDD |  |  |
|  |  |  | VDD |  |  |
|  |  |  |  |  |  |
| ZCalCompDAC[:0] |  |  | VDD |  | VREF code for Comparator offset compensation. |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
| ZCalAnaClk |  |  | VDD |  | Sampling clock for comparator Sense-amp |
| ZCalCompGainCurrAdj[5:0] |  |  | VDD |  | Bias Current Trim and Comparator gain control. Default is 6h’00 |
| ZCalCompGainResAdj |  |  | VDD |  | Comparator Gain Programmability with Resistor. Default is 1b’0 [ reserve pin] |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
| ZCalCompOut |  |  | VDD |  | Comparator output pin - provides comparator decision output |
| VDD |  |  | VDD | Async | Digital Logic Power Supply |
|  |  |  |  |  |  |
| VCCIO |  |  | VCCIO | Async | IO driver power supply for resistor DAC |
| VSS |  |  | GND | Async | Ground |

Table Notes:

- All reserved/unused pins should be driven to 0.
## Logical functionality

The following table summarizes the logical functionality of the macro

Table 3 Logical Functionality

| **ZCalAnaEn** | **ZCalCompEn** | **ZCal****En** | **ZCa****En** | **ZCal****En** | **Vpos** | **ZCalCompOut** | **Mode** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 0 | 0 | 0 | ref |  | Offset Calibration | 1 |
| 1 | 0 | 1 | 0 | 0 |  |  |  | 1 |
| 1 | 0 | 0 | 1 | 0 |  |  |  | 1 |
| 1 | 0 | 0 | 0 | 1 |  |  | Calibration | 1 |
| 1 | 0 | 0 | 0 | 0 | high-ohmic | x | Over-voltage Protection | 1,2 |
| 0 | x | x | x | x | x | 1 | Compensation OFF | 1 |

Table Notes:

- Vneg is always attached to Vdac
- Recommended codes for DFT state
## DFT

Input condition:

## Timing Diagram

The following figure shows the timing diagram for the FSM dwc__cmpana

TBD

Figure 3 ZCAL Sequencer FSM Timing Diagram

## Control Signals & Settling Time Allowances

- **The Calibration Select signals**, namely,
*dwc_**_cmpana/**ZCalCompEn**, *

*dwc_**_cmpana/**ZCal**En**, *

*dwc_**_cmpana/**ZCal**En**,*

*dwc_**_cmpana/**ZCal**En*

should always be either “ONE-HOT” or “ALL COLD”. All other states are illegal as they can cause electrical contention between *ZCal**Load**, ZCal**Load* or *Vref*.

The FSM drives the control signals to enable the analog comparator in different calibration modes.

The figure below shows the control signals for the analog comparator.

3

- **Check allowance for Startup Time **from startup circuit to all bias/analog nodes settles:
A minimum wait time (**ZCalCompStartupTime** - Section 5-4 Timing specification) is needed after *dwc_**_cmpana/**ZCalAnaEn** (**posedge** only) *occurs & prior to rising ZcalCompEn signal to enable Comparator Offset Calibration

3

- **Check allowance for Settling Time in Comparator Offset Calibration Mode**
A minimum wait time (**ZCalOffsetSampleTime**– Section 5-4 Timing specification) is needed for any desired changes on the key analog signals of the macro are ready to be sampled by the Sense-Amp. These changes can happen due to the following scenarios:

- Start of each calibration step and/or switching from one step to another, that is, transitions on *dwc_**_cmpana/**ZCalCompEn*
- FSM updates to internal DAC during the offset correction step, that is, transitions on
- *dwc_**_cmpana/**ZCalCompDAC**[**:0]*
So, this wait time needs to be observed from all of the above events (from whichever happens latest if they are in sequence) to the **first** **valid** sampling edge of *dwc_**_cmpana/**ZCalAnaClk*. Subsequent samples for digital averaging can be taken at full RefClk rate (0.5ns typical)

3

3

- **Check allowance for Settling Time of **** Calibration Modes**
3

3

A minimum wait time (**ZCalSampleTime** – Section 5-4 Timing specification) is needed for any desired changes on the key analog signals of the macro are ready to be sampled by Sense-Amp. These changes can happen due to the following scenarios:

- Start of each calibration step and/or switching from one step to another, that is, transitions on
*dwc_**_cmpana/**ZCal**En*

- FSM replica driver instances during all calibration steps other than the offset correction step
So, this wait time needs to be observed from all of the above events (from whichever happens latest if they are in sequence) to the **first** **valid** sampling edge of *dwc_**_cmpana/**ZCalAnaClk*. Subsequent samples for digital averaging can be taken at full RefClk rate (0.5ns typical)

3

3

## Impedance Calibration Code Scaling

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

ZCalScaleBaseZCalScaleNumZCalScaleDen

## and Vdac range

3

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

Table 3

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  | 0.5 * VCCIO |
|  |  |  |

3

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

3

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

3

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

# Detailed functionality

## Compensation Engine Operation

The calibration circuit is configured/monitored through ’s prefixed with ZCal.

When calibration is enabled, the Calibration Control FSM, located inside dwc_ddrphy_zcont.v, will send a signal to the Calibration FSM, inside dwc__zcal_ns.v, to start one calibration run.

Each calibration run follows the steps below:

- Enable ZCalAnaClk(CLKEN), then enable the analog circuit for calibration (starting CMPANA_ON)
- Wait for the analog circuit bias currents to stabilize (CMPANA_ON)
- Calibrate the comparator to cancel the comparator’s offset voltage (OFFSET_CAL)
- Calibrate the
- Calibrate
- Disable the analog circuit for calibration (CMPANA_OFF) and disable ZCalAnaClk(CLKDIS)
The figure below shows the FSM for the impedance calibration sequence

4

The calibration time (tZCal) (when ZCalStep = 1) is:

tZcal = Startup Time + CalOffset Time + Time + Cal Scaling Time + CalN Time + Cal Scaling Time

= ZCalCompStartupTime + Cal Scaling Time + 4 * NumberSteps * [(max (ZCalSampleTime, ZCalOffsetSampleTime) + ZCalNumVotes + 16]

- Number Steps = roundup ((final value code – initial value code)/8)) + [10 or 8]
Table 4 Init Code & Numbers Steps of calibration

| **PHY Build** | **Calibration Mode** | **Init_Code** | **Max Number Steps** | **Proposed ****No.Steps**** ****Specificaion****(Max)** | **Notes** |
| --- | --- | --- | --- | --- | --- |
| UCIE | **CalOffset** | *ZCalInitOffset** = * | Roundup ((117-0)/8) +10) = 25 | 40 | 1 |
|  | **CalP** | *ZCalInitPext**=* | Roundup ((117-34)/8) +10) = 37 | 40 | 1 |
|  | **CalN** | *ZCalInitNint**=* | Roundup ((134-0)/8) +8) = 25 | 40 | 1 |
|  | **Cal****ODT** | *ZCalInit**ODT**=* |  |  |  |

Table Notes:

- ZCalStep = 1: Step by 8 (and then by 1 during the final fine search).
The **maximum** calibration time (tZCal(max)) (when ZCalStep = 0) is:

tZcal(max) = Startup Time + CalOffset Time + CalP Time + Cal Scaling Time + CalN Time + Cal Scaling Time + CalODT Time

= ZCalCompStartupTime + Cal Scaling Time + 4 * 128 * [(max (ZCalSampleTime, ZCalOffsetSampleTime) + ZCalNumVotes + 16]

In which,

- ZCalStep CSR: Step size used during linear search algorithm. The ZCalStep CSR determines if the linear search will be done first with coarse steps of 8 followed by fine steps of 1, or if a step of 1 will be used throughout. Using the coarse/fine option speeds up the calibration.
- 0 = Step by 1.
- 1 = Step by 8 (and then by 1 during the final fine search).
- ZCalCompStartupTime: Settling time for comparator and DAC bias currents = 1 us
- ZCalSampleTime: Settling time for comparator during P and N calibration (250ns)
- ZCalOffsetSampleTime: Settling time for comparator during comparator offset calibration(200ns)
- ZCalNumVotes: Consecutive comparator output bits over which majority voting is done (Max=7, see more at section 4.1.3)
### Calibration Sequence

**Step #****[****OFFSET****]: Comparator Offset Correction**

**Purpose: ** For both pull-up/pull-down and ODT driver calibration

- Set = 1’b1 (selects Vref as the comparator reference; appears on ).
- Run a Linear Search on ZCalCompDAC[:0] starting from Initial Code (*ZCalInitOffset*) . The linear search will be done first with coarse steps of 8 followed by fine steps of 1, or if a step of 1 will be used throughout. (*Vote_result** module is referred to session 4.1.3)*
- Converge to the offset-corrected reference (Vdac).
- Store the converged DAC code (CompZCal)
4

4

4

4

**Step #****[****P****]: ****Pull-up Driver ****alibration**

**Purpose: ** For mission mode pull-up drivers

- Keep CompZCal as the comparator reference (appears on* **Vneg*)
- Set ZCalEn = 1’b1
- Store the converged pull-up **TxZCalP**
4

4

**Step #****[****NINT****]: **

4

Table 4 Replica Driver Settings for Various Calibration States

| **PHY Build** | **Calibration state** | **ZQCalCodePD** | **ZQCalCodePU** | **ODTCalCode** |
| --- | --- | --- | --- | --- |
| UCIE | Pull-up calibration |  | **TxZCalP** |  |
|  |  |  |  |  |
|  | ODT Calibration |  |  |  |

Table Notes:

- All unfilled cells in the table should be interpreted as “Don’t care”. They have deliberately been left blank to avoid clutter and showcase the important portions of the calibration.
- Text in **red** represent the result in each calibration step
### Vote_result

Please see more details at section 3.10 “zcal_vote Design Description” on the softip_zcal_design_specification.docx

### Additional RTL requirements

- For *all* offset correction steps above, since the comparator reference appears on *Vpos* (instead of *Vneg*), the SAR state machine should account for the polarity inversion in interpreting the comparator result.
- It is preferred that the switching between the ZCal(Comp/PU/PD/ODT)En signals is implemented as a break-before-make in the controller. For example, during transition from comparator offset calibration to driver pull up calibration, the controller should de-assert ZCalCompEn, wait briefly (~ 1 refclk period) and then assert ZCalPUEn. This ensures that any internal contention is avoided.
- The sampling clock for the comparator sense-amp can be allowed to toggle at the full *refclk* rate during the entire duration the compensation is active.
- *dwc_**_cmpana* wakeup wait time requirement:
Upon PHY power-up or every time *dwc_**_cmpana *is woken up for calibration (by asserting *dwc_**_cmpana/**ZCalAnaEn**)*, sufficient wait time (1000ns) needs to be allowed for the voltage references and current biases to settle before the comparator is ready to use.

4

| **Parameter** | **Symbol** | **Unit** | **Min** | **Typ** | **Max** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| Sampling Clock Period (for Pull-up/Pull-down Driver/Load Two-Point Calibration steps) | Tclk | ns |  |  | 0.5 | 1 |
| Sampling Clock Period (for Comparator Offset Correction step) | Tclk | ns |  |  | 0.5 | 1 |
| Settling Time | ZCalSampleTime | ns |  |  | 250 | 2 |
|  |  |  |  |  |  |  |
| Settling Time for Comparator Offset step | ZCalOffsetSampleTime | ns |  |  | 200 | 3 |
| StartupTime(Settling time for comparator and DAC bias currents) | ZCalCompStartupTime | us |  |  | 1 |  |
| Clk2q( CLK to Output delay) | CmprClk2Q | ps |  |  | 350 |  |

Table Notes:

- Spec is informational. This will be met by architectural construction in the Cmpdig FSM.
Sampling clock is divided down from RefClk (2GHz max). High time is one-half of the RefClk period.

- Defined as the minimum time between a Driver/ODT Process Compensation code update or switching of the calibration mux (at the start of calibration step) and the relevant comparator inputs settling to within 0.025% VCCIO from their steady-state values.
- Defined as the minimum time between a DAC code update or switching of the calibration mux (at the start of calibration step) and the relevant comparator inputs settling to within 0.025% VCCIO (1/10th of the accuracy targets for the raw reference and the DAC resolution) from their steady-state values.
## Macro Construction Details

*dwc_**_cmpana* performs the following functions in the overall compensation scheme:

- Provides a precision voltage reference programmable to over the range 0.43* to 0.66*.
- Provides a fine resolution DAC to generate an offset over a small correction voltage range around these Vref set-points. This DAC is used to null out the comparator’s inherent DC offset at the above set-points
- Houses a decoder for Vref generation and a decoder for the Offset Correction DAC
- Provides a very low-leakage analog mux to feed appropriate comparison voltages into the comparator’s inputs during each of the calibration steps
- Provides Analog RC filters (poly resistor, metal cap) to provide noise immunity on the sensitive comparator input nodes and reduce “LSB chatter” on the converged codes
- a clocked comparator to make calibration decisions
- CDM diode cells to protect the comparator input gates exposed to bump connections
Offset compensation is achieved by comparing the DAC output against the precision Vref for each test code of the SAR algorithm. The algorithm naturally searches for the *zero crossing* of the comparator and hence forces the DAC code to converge to the “offset-compensated Vref”. This setting is then used as the reference for all the subsequent driver calibration steps.

### Vref and Offset Generating DAC Construction

4

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

### Clocked Comparator

Table 4 Current bias generator states

| **ZCalAnaEn** | **VDD****/R ** **Bias** | **Notes** |
| --- | --- | --- |
| 0 | OFF | Compensation Inactive |
| 1 | ON | VDD/R bias in use (default) |

Table 4 Encoding for comparator bias current trim

| **ZCalCompGainCurrAdj****[7:4]****(2 MSBs are reserved and rest 2 are used for gain adjust)** | **Ibias** | **ZCalCompGainCurrAdj****[3:0]** |
| --- | --- | --- |
| Unused | 0% (nominal) | 0000 |
| Unused | -25% | 0001 |
| Unused | -50% | 0011 |
| Unused | +25% | 0100 |
| Unused | +50% | 1100 |

Table Notes:

- All %’s are relative additions to their respective nominal values
- All unused bits are tied to VSS
.

# Electrical Parameters

## 5.1 DC Specification

Table 5 System Calibration Budgets and Breakdown Targets

| **Parameter** | **Unit** | **Min** | **Max** | **Notes/Conditions** |
| --- | --- | --- | --- | --- |
| **Total NMOS Driver Calibration Budget: Target DC Resistance +/-10% of Target DC Resistance** |  |  |  |  |
| Finite Resolution of Driver Pull-down | % Target DC Res |  |  |  |
| Offset compensation accuracy of dwc__cmpana | % Target DC Res |  |  | 1 |
| Comparator sensitivity in dwc__cmpana | % Target DC Res |  |  | 2 |
| Mismatch across PHY | % Target DC Res |  |  | 3,6 |
| Package route/wiring | % Target DC Res |  |  |  |
| **Total PMOS Driver Calibration Budget: Target DC Resistance +/-10% of Target DC Resistance ** |  |  |  |  |
| Propagation error from Driver Pull-down Calibration | % Target DC Res |  |  | 4 |
| Finite Resolution of Driver Pull-up | % Target DC Res |  |  |  |
| Comparator sensitivity in dwc__cmpana | % Target DC Res |  |  | 2 |
| Mismatch across PHY | % Target DC Res |  |  | 3,6 |
| Local mismatch between driver copies used for calibration, Package route/wiring | % Target DC Res |  |  |  |

Table Notes:

- (Calibration DAC Resolution + Internal VREF Accuracy + Comparator Sensitivity + Settling Accuracy) during offset compensation step.
- (Comparator Sensitivity + Settling Accuracy) during NMOS calibration step. Note that this error source also propagates as residue from offset compensation step and hence gets counted twice.
- 3-sigma across-chip statistics. Assuming intercept (2%) due to large physical geometry of driver elements, dominated by resistor variation (MOS<30%) and √2 as mismatch multiplier.
- Finite Resolution of NMOS Driver. Comparator Offset Residue affects only NMOS driver calibration. It naturally nulls itself out during PMOS driver calibration.
- VTERM spec of (50% +/- 2.5%)* translates to a RPODT mismatch spec of being within +/-10% of RNODT. Since the driver is configured as ODT, the DC balance is primarily determined by finite resolution of Driver Pull-up. There is NO propagation error term from Driver Pull-down Calibration since it is only a relative/mismatch spec.
- All standard deviation numbers are specified as a double-sided sigma symmetrically distributed about the mean. ie, 3-sigma statistics refers to yield corresponding to +/-3sigma points (a full 6-sigma span) on the Gaussian distribution.
Table 5 Calibration Budget and Breakdown Targets

| **Parameter** | **Symbol** | **Unit** | **Min** | **Typ** | **Max** | **Notes/Conditions** |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |
| **Total Offset Compensation Error Budget : +/-****(****TBD****)****% of target resistance (equivalent to +/-****(****TBD****)****% of V****CCIO****)** |  |  |  |  |  |  |  |
| Calibration DAC Resolution | VdacRelStep | %VCCIO | 0 |  | 0.25% | 1 |  |
| Calibration VREF Accuracy | VrefRelErr | %VCCIO | -0.5% |  | 0.5% | 2 |  |
| Settling Accuracy | SettlingErr | %VCCIO | -0.025% |  | 0.025% | 3 |  |
| Comparator Sensitivity | CmprSens | %VCCIO | 0.5% |  |  | 4 |  |
| Offset Compensation Range | VdacRng | %VCCIO | 43 |  | 66 | 5,6 |  |

Table Notes:

- Equivalent to 1mV resolution at VCCIO=0.5V. Also, includes 3-sigma statistical variation.
- Equivalent to ±2mV accuracy around target VREF at =0.4V. Also, includes 3-sigma statistical variation.
- Applies to both settling of Calibration DAC output during CalCmpr step and of the active calibration node during subsequent steps. Settling time is specified as time taken to settle to within 0.025% VCCIO from the final value.
- Defined as one-half of the DC hysteresis window of the comparator. Equivalent to 2mV sensitivity at VCCIO=0.5V.
- Defined as (top of scale – bottom of scale) of Calibration DAC. Equivalent to ±17% range at VCCIO=0.5V
- Assumes comparator 3-sigma offset not to exceed 40mV (1-sigma < 13mV). If simulations indicate a higher offset, Cmpdig RTL can be modified to extend the correction range using the overlap available across adjacent Vref taps.
- All standard deviation numbers are specified as a double-sided sigma symmetrically distributed about the mean. , 3-sigma statistics refers to yield corresponding to +/-3sigma points (6-sigma span) on the Gaussian distribution.
## AC Specification

Table 5 AC specification

| **Parameter** | **Symbol** | **Unit** | **Min** | **Typ** | **Max** | **Notes/Conditions** |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |
| Analog Filter Bandwidth | AnaFiltBw | MHz | 10 |  | - | 1 |  |

Table Notes:

- Equivalent target time constants are 4ns (Min) and 16ns (Max).
## Power Specification

Table 5 Power Specification

| **Parameter** | **Symbol** | **Unit** | **Min** | **Typ** | **Max** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| VDD Peak Current (Mission Mode, compensation active) | ICalbrON_Peak_VDD | mA |  |  | 6 |  |
| VDD Current (Mission Mode, compensation active) | ICalbrON_VDD | mA |  |  | 1 |  |
| VDD Current (Mission Mode, compensation inactive) | ICalbrOFF_VDD | uA |  |  | 50 |  |
| VDD Current (LP3 Mode) | ICalbrLP3_VDD | uA |  |  | 1 |  |
| VCCIO Peak Current (Mission Mode, compensation active) | ICalbrON_Peak_VCCIO | uA |  |  | 100 | 1 |
| VCCIO Current (Mission Mode, compensation active) | ICalbrON_VCCIO | uA |  |  | 50 | 1 |
| VCCIO Current (Mission Mode, compensation inactive) | ICalbrOFF_VCCIO | uA |  |  | 20 | 1 |
| VCCIO Current (LP3 Mode) | ICalbrLP3_VCCIO | uA |  |  | 20 | 1 |

Table Notes:

- DAC decoder
# RTL and Timing Constraints

6

| **Parameter** | **Symbol** | **Unit** | **Min** | **Typ** | **Max** | **Notes** |
| --- | --- | --- | --- | --- | --- | --- |
| Sampling Clock Period (for Pull-up/Pull-down Driver/Load Two-Point Calibration steps) | Tclk | ns |  |  | 0.5 | 1 |
| Sampling Clock Period (for Comparator Offset Correction step) | Tclk | ns |  |  | 0.5 | 1 |
| Settling Time (for Pull-up/Pull-down Driver/Load/) | ZCalSampleTime | ns |  |  | 250 | 2 |
| Settling Time (for Comparator Offset Correction step) | ZCalOffsetSampleTime | ns |  |  | 200 | 3 |
| StartupTime(Settling time for comparator and DAC bias currents) | ZCalCompStartupTime | us |  |  | 1 |  |

Table Notes:

- Spec is informational. This will be met by architectural construction in the Cmpdig FSM.
- Sampling clock is divided down from RefClk (2GHz max). High time is one-half of the RefClk period.
- Defined as the minimum time between a Driver/ODT Process Compensation code update or switching of the calibration mux (at the start of calibration step) and the relevant comparator inputs settling to within 0.025% VCCIO from their steady-state values.
- Defined as the minimum time between a DAC code update or switching of the calibration mux (at the start of calibration step) and the relevant comparator inputs settling to within 0.025% VCCIO (1/10th of the accuracy targets for the raw reference and the DAC resolution) from their steady-state values.
# Simulation Results

## Simulation Results vs. Specification

Table 7 Simulation Results

## R-die C-die

## PowerEM/PowerIR/SigEM Results

# Simulation Plan

## Corners & verification conditions

Corners Simulation: TT/SS/FF/SF/FS

Table 8 Condition for design performance verification

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VDD | Core supply Voltage, normal range | 0.6375 | 0.75 | 0.8625 | V |
| VCCIO | Driver supply Voltage (normal mode) | 0.425/0.595 | 0.5/0.7 | 0.575/0.805 | V |
| **VSS** | Core ground | 0 | 0 | 0 | V |
| **Tj** | Junction temperature | -40 | 25 | 125 | C |

## Test-benches list

The shows the verification test bench:

|  |  |
| --- | --- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

# Integration Guideline

## External Resistor:

We do not have specific requirement for each parasitic. The resistance of external resistor is Ω +/, includes:​

- arasitic from BP_ZN note to C4 Bumps​ (1)
- arasitic on packaging (from C4 bump to BGA ball (2)
- arasitic on PCB from BGA ball to external resistor (both 2 nodes of external resistor (3)​
- xternal resistor variation itself​(4)
2Ohm ≤ Resistance (1) + Resistance (2) + Resistance (3) + External resistor ≤ Ohm

**Notes: IF the parasitic is out of range, please adjust the External Resistor value accordingly.**

9

| **Symbol****​** | **Description****​** | **M** |  |  | **Unit****​** |
| --- | --- | --- | --- | --- | --- |
|  | External resistor value, including:​ parasitic from BP_ZN note to C4 Bumps​ (1) parasitic on packaging (from C4 bump to BGA ball)​ (2) parasitic on PCB from BGA ball to external resistor (both 2 nodes of external resistor)​ (3) external resistor variation itself​ (4)(tolerance <=0.1%) | 2 |  |  | Ω​ |

## Connection of TXIMP/RX & CMPANA inside MSCTRL

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |

Refer: dwc__io_tx_databook.docx, dwc__io_rx_databook.docx

|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

9

9
