"""OpenFFS CLI - main entry point."""
import argparse, json, sys
from pathlib import Path
from datetime import datetime


def cmd_version(args):
    import openffs
    print(f"OpenFFS v{openffs.__version__}"); print(f"Standard: {openffs.__edition__}")


def cmd_standards(args):
    from openffs.standards.notifier import check_currency, format_notifications
    print(format_notifications(check_currency()))


def cmd_project(args):
    import openffs
    if args.action == "new":
        name = args.name or "openffs_project"; cwd = Path.cwd() / name
        cwd.mkdir(exist_ok=True)
        (cwd / "openffs.json").write_text(json.dumps({"project_name": name,
            "openffs_version": openffs.__version__, "edition": openffs.__edition__}, indent=2))
        print(f"Created project: {cwd}")
    elif args.action == "show":
        cfg = Path.cwd() / "openffs.json"
        print(cfg.read_text() if cfg.exists() else "No openffs.json in current directory.")


def cmd_assess(args):
    from openffs.api579.part4.assessment import assess_metal_loss
    from openffs.api579.part5.assessment import assess_gouge_level1
    from openffs.api579.part14.assessment import assess_structural_member
    in_file = Path(args.input or "components.json")
    if not in_file.exists(): print(f"ERROR: {in_file} not found", file=sys.stderr); sys.exit(1)
    data = json.loads(in_file.read_text())
    components = data if isinstance(data, list) else data.get("components", [])
    print(f"Loaded {len(components)} component(s).")
    out_path = Path(args.output or "results.json")
    results = []
    for comp in components:
        cid = comp.get("id") or comp.get("component_id") or "unknown"
        track = comp.get("track", "structural"); lvl = args.level if args.level else comp.get("level", 1)
        try:
            if track == "pressure":
                if comp.get("kind") == "gouge":
                    res = assess_gouge_level1(component_id=cid, D=float(comp["D_mm"]),
                        tnom=float(comp["tnom_mm"]), tloss_avg=float(comp.get("tloss_avg_mm", 0)),
                        fc=float(comp.get("fc_mm", 0)), P=float(comp["P_MPa"]),
                        S=float(comp["S_MPa"]), E=float(comp.get("E", 1.0)),
                        L=float(comp.get("gouge_L_mm", 0)), W=float(comp.get("gouge_W_mm", 0)),
                        depth=float(comp.get("gouge_depth_mm", 0)))
                else:
                    geom = comp.get("geometry", "cylindrical")
                    kwargs = dict(component_id=cid, geometry=geom, D=float(comp["D_mm"]),
                        tnom=float(comp["tnom_mm"]), tloss=float(comp.get("tloss_mm", 0)),
                        fc=float(comp.get("fc_mm", 0)), P=float(comp["P_MPa"]),
                        S=float(comp["S_MPa"]), E=float(comp.get("E", 1.0)),
                        CR=float(comp.get("CR_mm_per_yr", 0)), tnext=float(comp.get("tnext_yr", 0)))
                    for k in ("alpha_deg", "L_head", "r_knuckle", "h_head"):
                        if k in comp: kwargs[k] = comp[k]
                    res = assess_metal_loss(**kwargs)
            elif track == "structural":
                res = assess_structural_member(component_id=cid, section_designation=comp["section"],
                    member_type=comp.get("member_type", "brace"),
                    demand_moment=float(comp.get("demand_M_Nmm", 0)),
                    demand_shear=float(comp.get("demand_V_N", 0)),
                    demand_axial=float(comp.get("demand_N_N", 0)),
                    hardness_hb=float(comp["HB"]), gouges=comp.get("gouges"),
                    perforations=comp.get("perforations"), level=lvl)
            else: print(f"Unknown track: {track} for {cid}", file=sys.stderr); continue
            results.append(res.to_dict())
            verb = "ESCALATE" if res.requires_escalation else ("SUITABLE" if res.is_suitable else res.suitability)
            print(f"  {cid}: {verb}")
        except Exception as e:
            print(f"  {cid}: ERROR - {e}", file=sys.stderr)
    out_path.write_text(json.dumps({"openffs_version": "0.7.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "level": args.level, "results": results}, indent=2))
    print(f"\nResults written to: {out_path}")


def cmd_report(args):
    from openffs.reporting.text import render_text_report, render_html_report, render_pdf_report
    from openffs.core.result import AssessmentResult
    in_path = Path(args.input or "results.json")
    if not in_path.exists(): print(f"ERROR: {in_path} not found", file=sys.stderr); sys.exit(1)
    data = json.loads(in_path.read_text())
    raw = data.get("results", data) if isinstance(data, dict) else data
    results = [AssessmentResult(component_id=r["component_id"], track=r["track"],
        level=r["level"], suitability=r["suitability"], governing_clause=r["governing_clause"],
        rsf=r.get("rsf"), mawp=r.get("mawp"), remaining_life=r.get("remaining_life"),
        dc_ratio=r.get("dc_ratio"), inputs_echo=r.get("inputs_echo", {}),
        calculation_log=r.get("calculation_log", []), warnings=r.get("warnings", []),
        metadata=r.get("metadata", {})) for r in raw]
    fmt = args.format or "txt"
    if args.output is None: ext = "pdf" if fmt == "pdf" else "html" if fmt == "html" else "txt"; args.output = f"report.{ext}"
    project = data.get("project_name", "OpenFFS Assessment") if isinstance(data, dict) else "OpenFFS Assessment"
    out_path = Path(args.output)
    if fmt == "txt": out_path.write_text(render_text_report(results, project))
    elif fmt == "html": out_path.write_text(render_html_report(results, project))
    elif fmt == "pdf":
        if not render_pdf_report(results, str(out_path), project):
            print("PDF requires reportlab. Falling back to txt.", file=sys.stderr)
            out_path = Path("report.txt"); out_path.write_text(render_text_report(results, project))
    print(f"Report written to: {out_path}")


def cmd_license(args):
    from openffs.licensing import load_license, save_license, issue_license, FEATURE_PRO_PARTS_FULL, FEATURE_PRO_PDF, FEATURE_PRO_LIVE_STANDARDS
    lic = load_license()
    if args.action == "show":
        print(f"Licensee:  {lic.licensee}"); print(f"Tier:      {lic.tier}"); print(f"Seats:     {lic.seats}")
        print(f"Features:  {', '.join(sorted(lic.features)) if lic.features else '(community)'}")
        print(f"Issued:    {lic.issued_at}"); print(f"Expires:   {lic.expires_at}")
    elif args.action == "generate_demo":
        demo = issue_license(licensee=args.licensee or "Demo User", tier="pro", seats=10,
            features=frozenset([FEATURE_PRO_PARTS_FULL, FEATURE_PRO_PDF, FEATURE_PRO_LIVE_STANDARDS]))
        path = save_license(demo); print(f"Generated Pro license (demo): {path}")


def build_parser():
    parser = argparse.ArgumentParser(prog="openffs", description="OpenFFS CLI")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version"); sub.add_parser("standards")
    p_proj = sub.add_parser("project"); p_proj.add_argument("action", choices=["new", "show"]); p_proj.add_argument("--name")
    p_assess = sub.add_parser("assess"); p_assess.add_argument("--level", type=int, choices=[1, 2, 3], default=1)
    p_assess.add_argument("--all", action="store_true"); p_assess.add_argument("--only-failed", action="store_true")
    p_assess.add_argument("--input"); p_assess.add_argument("--output")
    p_rep = sub.add_parser("report"); p_rep.add_argument("--format", choices=["txt", "html", "pdf"], default="txt")
    p_rep.add_argument("--input"); p_rep.add_argument("--output")
    p_lic = sub.add_parser("license"); p_lic.add_argument("action", choices=["show", "generate_demo", "install"])
    p_lic.add_argument("--licensee"); p_lic.add_argument("--key-file")
    return parser


def main(argv=None):
    parser = build_parser(); args = parser.parse_args(argv)
    if args.command is None: parser.print_help(); return 0
    dispatch = {"version": cmd_version, "standards": cmd_standards, "project": cmd_project,
                "assess": cmd_assess, "report": cmd_report, "license": cmd_license}
    dispatch.get(args.command, lambda a: None)(args); return 0


if __name__ == "__main__": sys.exit(main())
