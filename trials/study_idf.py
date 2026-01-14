from dataclasses import dataclass
from msd2.eplus.main import layout_to_idf
from msd2.paths import DynamicPaths


@dataclass
class StudyIDF:
    case: str

    def inpath(self):
        return DynamicPaths.workflow_outputs / self.case / "ymove/out.json"

    def outpath(self):
        return DynamicPaths.workflow_outputs / self.case / "model"

    def gen_idf(self):
        layout_to_idf(self.inpath(), self.outpath())


if __name__ == "__main__":
    s = StudyIDF("")
    s.gen_idf()
