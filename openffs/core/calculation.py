"""Calculation log - audit trail for every assessment step."""


class CalculationStep:
    def __init__(self, step_number, equation_id, description, inputs, result, units=""):
        self.step_number = step_number; self.equation_id = equation_id
        self.description = description; self.inputs = dict(inputs)
        self.result = result; self.units = units


class CalculationLog:
    def __init__(self):
        self.steps = []; self._counter = 0
    def add(self, equation_id, description, inputs, result, units=""):
        self._counter += 1
        step = CalculationStep(self._counter, equation_id, description, dict(inputs), result, units)
        self.steps.append(step); return step
    def to_lines(self):
        out = []
        for s in self.steps:
            in_str = ", ".join(f"{k}={v}" for k, v in s.inputs.items())
            out.append(f"  Step {s.step_number} [{s.equation_id}]: {s.description}")
            out.append(f"      inputs:  {in_str}")
            out.append(f"      result:  {s.result} {s.units}".rstrip())
        return out
    def to_plain(self):
        out = []
        for s in self.steps:
            in_str = ", ".join(f"{k}={v}" for k, v in s.inputs.items())
            out.append(f"[{s.equation_id}] {s.description}: {in_str} -> {s.result}")
        return out
    def __len__(self): return len(self.steps)
