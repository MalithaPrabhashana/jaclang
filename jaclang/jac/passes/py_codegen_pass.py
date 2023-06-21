"""Transpilation pass for Jaseci Ast."""
from typing import List

import jaclang.jac.jac_ast as ast
from jaclang.jac.jac_ast import AstNode
from jaclang.jac.passes.ir_pass import Pass


class PyCodeGenPass(Pass):
    """Jac transpilation to python pass."""

    marked_incomplete: List[str] = []

    def __init__(self) -> None:
        """Initialize pass."""
        self.indent_size = 4
        self.indent_level = 0
        self.cur_arch = None  # tracks current architype during transpilation
        super().__init__()

    def enter_node(self, node: AstNode) -> None:
        """Enter node."""
        if node:
            node.meta["py_code"] = ""
        return Pass.enter_node(self, node)

    def indent_str(self, indent_delta: int) -> str:
        """Return string for indent."""
        return " " * self.indent_size * (self.indent_level + indent_delta)

    def emit_ln(self, node: AstNode, s: str, indent_delta: int = 0) -> None:
        """Emit code to node."""
        node.meta["py_code"] += (
            self.indent_str(indent_delta)
            + s.replace("\n", "\n" + self.indent_str(indent_delta))
            + "\n"
        )

    def emit(self, node: AstNode, s: str) -> None:
        """Emit code to node."""
        node.meta["py_code"] += s

    def access_check(self, node: ast.OOPAccessNode) -> None:
        """Check if node uses access."""
        if node.access:
            self.warning(
                f"Line {node.line}, Access specifiers not supported in bootstrap Jac."
            )

    def decl_def_warn(self) -> None:
        """Warn about declaration."""
        self.warning(
            "Separate declarations and definitions not supported in bootstrap Jac."
        )

    def ds_feature_warn(self) -> None:
        """Warn about feature."""
        self.warning("Data spatial features not supported in bootstrap Jac.")

    def exit_token(self, node: ast.Token) -> None:
        """Sub objects.

        name: str,
        value: str,
        """
        self.emit(node, node.value)

    def exit_parse(self, node: ast.Parse) -> None:
        """Sub objects.

        name: str,
        """
        self.error("Parse node should not be in this AST!!")
        raise ValueError("Parse node should not be in AST after being Built!!")

    def exit_module(self, node: ast.Module) -> None:
        """Sub objects.

        name: str,
        doc: Token,
        body: "Elements",
        """
        self.emit_ln(node, node.doc.value)
        self.emit(node, node.body.meta["py_code"])
        self.ir = node

    def exit_elements(self, node: ast.Elements) -> None:
        """Sub objects.

        elements: List[GlobalVars | Test | ModuleCode | Import | Architype | Ability | AbilitySpec],
        """
        for i in node.elements:
            self.emit(node, i.meta["py_code"])

    @Pass.incomplete
    def exit_global_vars(self, node: ast.GlobalVars) -> None:
        """Sub objects.

        doc: "DocString",
        access: Optional[Token],
        assignments: "AssignmentList",
        """
        self.access_check(node)
        self.emit_ln(node, node.assignments.meta["py_code"])

    @Pass.incomplete
    def exit_test(self, node: ast.Test) -> None:
        """Sub objects.

        name: Token,
        doc: "DocString",
        description: Token,
        body: "CodeBlock",
        """
        self.warning(f"Line {node.line}, Test feature not supported in bootstrap Jac.")

    def exit_module_code(self, node: ast.ModuleCode) -> None:
        """Sub objects.

        doc: "DocString",
        body: "CodeBlock",
        """
        self.emit(node, node.doc.meta["py_code"])
        self.emit(node, node.body.meta["py_code"])

    def exit_doc_string(self, node: ast.DocString) -> None:
        """Sub objects.

        value: Optional[Token],
        """
        if type(node.value) == ast.Token:
            self.emit_ln(node, node.value.value)

    @Pass.incomplete
    def exit_import(self, node: ast.Import) -> None:
        """Sub objects.

        lang: Token,
        path: "ModulePath",
        alias: Optional[Token],
        items: Optional["ModuleItems"],
        is_absorb: bool,  # For includes
        """
        if node.lang.value != "py":
            self.warning(
                f"Line {node.line}, Importing non-python modules not supported in bootstrap Jac."
            )
        if node.is_absorb:
            self.warning(f"Line {node.line}, Includes not supported in bootstrap Jac.")
        if not node.items:
            if not node.alias:
                self.emit_ln(node, f"import {node.path.meta['py_code']}")
            else:
                self.emit_ln(
                    node,
                    f"import {node.path.meta['py_code']} as {node.alias.meta['py_code']}",
                )
        else:
            self.emit_ln(
                node,
                f"from {node.path.meta['py_code']} import {node.items.meta['py_code']}",
            )

    def exit_module_path(self, node: ast.ModulePath) -> None:
        """Sub objects.

        path: List[Token],
        """
        self.emit(node, "".join([i.value for i in node.path]))

    def exit_module_items(self, node: ast.ModuleItems) -> None:
        """Sub objects.

        items: List["ModuleItem"],
        """
        self.emit(node, ", ".join([i.meta["py_code"] for i in node.items]))

    def exit_module_item(self, node: ast.ModuleItem) -> None:
        """Sub objects.

        name: Token,
        alias: Optional[Token],
        """
        if type(node.alias) == ast.Token:
            self.emit(node, node.name.value + " as " + node.alias.value)
        else:
            self.emit(node, node.name.value)

    @Pass.incomplete
    def exit_architype(self, node: ast.Architype) -> None:
        """Sub objects.

        name: Token,
        typ: Token,
        doc: DocString,
        access: Optional[Token],
        base_classes: "BaseClasses",
        body: "ArchBlock",
        """
        self.access_check(node)
        if not node.base_classes:
            self.emit_ln(node, f"class {node.name.meta['py_code']}:")
        else:
            self.emit_ln(
                node,
                f"class {node.name.meta['py_code']}({node.base_classes.meta['py_code']}):",
            )
        self.emit_ln(node, node.doc.meta["py_code"], indent_delta=1)
        self.emit(node, node.body.meta["py_code"])

    @Pass.incomplete
    def exit_arch_decl(self, node: ast.ArchDecl) -> None:
        """Sub objects.

        doc: DocString,
        access: Token,
        typ: Token,
        name: Token,
        base_classes: "BaseClasses",
        self.def_link: Optional["ArchDef"] = None
        """
        self.decl_def_warn()

    @Pass.incomplete
    def exit_arch_def(self, node: ast.ArchDef) -> None:
        """Sub objects.

        doc: DocString,
        mod: Token,
        arch: "ObjectRef | NodeRef | EdgeRef | WalkerRef",
        body: "ArchBlock",
        """
        self.decl_def_warn()

    def exit_base_classes(self, node: ast.BaseClasses) -> None:
        """Sub objects.

        base_classes: List[Token],
        """
        self.emit(node, ", ".join([i.value for i in node.base_classes]))

    @Pass.incomplete
    def exit_ability(self, node: ast.Ability) -> None:
        """Sub objects.

        name: Token,
        is_func: bool,
        doc: DocString,
        access: Optional[Token],
        signature: FuncSignature | TypeSpec,
        body: CodeBlock,
        """
        self.access_check(node)
        self.emit_ln(node, f"def {node.name.value}{node.signature.meta['py_code']}:")
        self.emit_ln(node, node.doc.meta["py_code"], indent_delta=1)
        self.emit(node, node.body.meta["py_code"])

    @Pass.incomplete
    def exit_ability_decl(self, node: ast.AbilityDecl) -> None:
        """Sub objects.

        doc: DocString,
        access: Optional[Token],
        name: Token,
        signature: FuncSignature | TypeSpec,
        is_func: bool,
        """
        self.decl_def_warn()

    @Pass.incomplete
    def exit_ability_def(self, node: ast.AbilityDef) -> None:
        """Sub objects.

        doc: DocString,
        mod: Optional[Token],
        ability: AbilityRef,
        body: CodeBlock,
        """
        self.decl_def_warn()

    @Pass.incomplete
    def exit_ability_spec(self, node: ast.AbilitySpec) -> None:
        """Sub objects.

        doc: DocString,
        name: Token,
        arch: ObjectRef | NodeRef | EdgeRef | WalkerRef,
        mod: Optional[Token],
        signature: Optional[FuncSignature],
        body: CodeBlock,
        """
        self.decl_def_warn()

    @Pass.incomplete
    def exit_arch_block(self, node: ast.ArchBlock) -> None:
        """Sub objects.

        members: List[ArchHas | ArchCan | ArchCanDecl ],
        """
        for i in node.members:
            self.emit_ln(node, i.meta["py_code"])

    def exit_arch_has(self, node: ast.ArchHas) -> None:
        """Sub objects.

        doc: DocString,
        access: Optional[Token],
        vars: HasVarList,
        self.h_id = HasVar.counter
        """
        self.emit_ln(node, f"def has_{node.h_id}:")
        self.emit_ln(node, node.doc.meta["py_code"], indent_delta=1)
        self.emit_ln(node, node.vars.meta["py_code"], indent_delta=1)

    def exit_has_var_list(self, node: ast.HasVarList) -> None:
        """Sub objects.

        vars: List[HasVar],
        """
        for i in node.vars:
            self.emit_ln(node, i.meta["py_code"])

    def exit_has_var(self, node: ast.HasVar) -> None:
        """Sub objects.

        name: Token,
        type_tag: TypeSpec,
        value: Optional[AstNode],
        """
        if node.value:
            self.emit(
                node,
                f"self.{node.name.value}: {node.type_tag.meta['py_code']} = {node.value.meta['py_code']}",
            )
        else:
            self.emit(
                node, f"self.{node.name.value}: {node.type_tag.meta['py_code']} = None"
            )

    def exit_type_spec(self, node: ast.TypeSpec) -> None:
        """Sub objects.

        typ: Token,
        list_nest: TypeSpec,
        dict_nest: TypeSpec,
        """
        if node.dict_nest:
            self.emit(
                node,
                f"Dict[{node.list_nest.meta['py_code']}, {node.dict_nest.meta['py_code']}]",
            )
        elif node.list_nest:
            self.emit(node, f"List[{node.list_nest.meta['py_code']}]")
        else:
            self.emit(node, node.typ.value)

    @Pass.incomplete
    def exit_arch_can(self, node: ast.ArchCan) -> None:
        """Sub objects.

        name: Token,
        doc: DocString,
        access: Optional[Token],
        signature: Optional[EventSignature | FuncSignature],
        body: CodeBlock,
        """
        self.access_check(node)
        if node.signature:  # Error for EventSignature in EventSignature
            self.emit_ln(
                node, f"def {node.name.value}{node.signature.meta['py_code']}:"
            )
        else:
            self.emit_ln(node, f"def {node.name.value}():")
        self.emit_ln(node, node.doc.meta["py_code"], indent_delta=1)
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    @Pass.incomplete
    def exit_arch_can_decl(self, node: ast.ArchCanDecl) -> None:
        """Sub objects.

        name: Token,
        doc: DocString,
        access: Optional[Token],
        signature: Optional[EventSignature | FuncSignature],
        """
        self.decl_def_warn()

    @Pass.incomplete
    def exit_event_signature(self, node: ast.EventSignature) -> None:
        """Sub objects.

        event: Token,
        arch_tag_info: Optional[NameList | Token],
        """
        self.error("Event style abilities not supported in bootstrap Jac")

    def exit_name_list(self, node: ast.NameList) -> None:
        """Sub objects.

        names: List[Token],
        """
        self.emit(node, ", ".join([i.value for i in node.names]))

    def exit_func_signature(self, node: ast.FuncSignature) -> None:
        """Sub objects.

        params: Optional[FuncParams],
        return_type: Optional[TypeSpec],
        """
        self.emit(node, "(")
        if node.params:
            self.emit(node, node.params.meta["py_code"])
        self.emit(node, ")")
        if node.return_type:
            self.emit(node, f" -> {node.return_type.meta['py_code']}")

    def exit_func_params(self, node: ast.FuncParams) -> None:
        """Sub objects.

        params: List["ParamVar"],
        """
        first_out = False
        for i in node.params:
            self.emit(node, ", ") if first_out else None
            self.emit(node, i.meta["py_code"])
            first_out = True

    def exit_param_var(self, node: ast.ParamVar) -> None:
        """Sub objects.

        name: Token,
        type_tag: TypeSpec,
        value: Optional[AstNode],
        """
        if node.value:
            self.emit(
                node,
                f"{node.name.value}: {node.type_tag.meta['py_code']} = {node.value.meta['py_code']}",
            )
        else:
            self.emit(node, f"{node.name.value}: {node.type_tag.meta['py_code']}")

    def exit_code_block(self, node: ast.CodeBlock) -> None:
        """Sub objects.

        stmts: List["StmtType"],
        """
        self.emit(node, "\n")
        for i in node.stmts:
            self.emit_ln(node, i.meta["py_code"], indent_delta=1)

    def exit_if_stmt(self, node: ast.IfStmt) -> None:
        """Sub objects.

        condition: ExprType,
        body: CodeBlock,
        elseifs: Optional[ElseIfs],
        else_body: Optional[ElseStmt],
        """
        self.emit_ln(node, f"if {node.condition.meta['py_code']}:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)
        if node.elseifs:
            self.emit_ln(node, node.elseifs.meta["py_code"])
        if node.else_body:
            self.emit_ln(node, node.else_body.meta["py_code"])

    def exit_else_ifs(self, node: ast.ElseIfs) -> None:
        """Sub objects.

        elseifs: List[IfStmt],
        """
        for i in node.elseifs:
            self.emit_ln(node, f"elif {i.condition.meta['py_code']}:")
            self.emit_ln(node, i.body.meta["py_code"], indent_delta=1)

    def exit_else_stmt(self, node: ast.ElseStmt) -> None:
        """Sub objects.

        body: CodeBlock,
        """
        self.emit_ln(node, "else:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_try_stmt(self, node: ast.TryStmt) -> None:
        """Sub objects.

        body: CodeBlock,
        excepts: Optional[ExceptList],
        finally_body: Optional[FinallyStmt],
        """
        self.emit_ln(node, "try:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)
        if node.excepts:
            self.emit_ln(node, node.excepts.meta["py_code"])
        if node.finally_body:
            self.emit_ln(node, node.finally_body.meta["py_code"])

    def exit_except(self, node: ast.Except) -> None:
        """Sub objects.

        typ: ExprType,
        name: Optional[Token],
        body: CodeBlock,
        """
        if node.name:
            self.emit_ln(
                node, f"except {node.typ.meta['py_code']} as {node.name.value}:"
            )
        else:
            self.emit_ln(node, f"except {node.typ.meta['py_code']}:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_except_list(self, node: ast.ExceptList) -> None:
        """Sub objects.

        excepts: List[Except],
        """
        for i in node.excepts:
            self.emit_ln(node, i.meta["py_code"])

    def exit_finally_stmt(self, node: ast.FinallyStmt) -> None:
        """Sub objects.

        body: CodeBlock,
        """
        self.emit_ln(node, "finally:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_iter_for_stmt(self, node: ast.IterForStmt) -> None:
        """Sub objects.

        iter: Assignment,
        condition: ExprType,
        count_by: ExprType,
        body: CodeBlock,
        """
        self.emit_ln(node, f"{node.iter.meta['py_code']}")
        self.emit_ln(node, f"while {node.condition.meta['py_code']}:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)
        self.emit_ln(node, f"{node.count_by.meta['py_code']}", indent_delta=1)

    def exit_in_for_stmt(self, node: ast.InForStmt) -> None:
        """Sub objects.

        name: Token,
        collection: ExprType,
        body: CodeBlock,
        """
        self.emit_ln(
            node, f"for {node.name.value} in {node.collection.meta['py_code']}:"
        )
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_dict_for_stmt(self, node: ast.DictForStmt) -> None:
        """Sub objects.

        k_name: Token,
        v_name: Token,
        collection: ExprType,
        body: CodeBlock,
        """
        self.emit_ln(
            node,
            f"for {node.k_name.value}, {node.v_name.value} in {node.collection.meta['py_code']}.items():",
        )
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_while_stmt(self, node: ast.WhileStmt) -> None:
        """Sub objects.

        condition: ExprType,
        body: CodeBlock,
        """
        self.emit_ln(node, f"while {node.condition.meta['py_code']}:")
        self.emit_ln(node, node.body.meta["py_code"], indent_delta=1)

    def exit_raise_stmt(self, node: ast.RaiseStmt) -> None:
        """Sub objects.

        cause: Optional[ExprType],
        """
        if node.cause:
            self.emit_ln(node, f"raise {node.cause.meta['py_code']}")
        else:
            self.emit_ln(node, "raise")

    def exit_assert_stmt(self, node: ast.AssertStmt) -> None:
        """Sub objects.

        condition: ExprType,
        error_msg: Optional[ExprType],
        """
        if node.error_msg:
            self.emit_ln(
                node,
                f"assert {node.condition.meta['py_code']}, {node.error_msg.meta['py_code']}",
            )
        else:
            self.emit_ln(node, f"assert {node.condition.meta['py_code']}")

    @Pass.incomplete
    def exit_ctrl_stmt(self, node: ast.CtrlStmt) -> None:
        """Sub objects.

        ctrl: Token,
        """
        if node.ctrl.value == "skip":
            self.error("skip is not supported in bootstrap Jac")
        else:
            self.emit_ln(node, node.ctrl.value)

    def exit_delete_stmt(self, node: ast.DeleteStmt) -> None:
        """Sub objects.

        target: ExprType,
        """
        self.emit_ln(node, f"del {node.target.meta['py_code']}")

    @Pass.incomplete
    def exit_report_stmt(self, node: ast.ReportStmt) -> None:
        """Sub objects.

        expr: ExprType,
        """
        self.ds_feature_warn()

    @Pass.incomplete  # Need to have validation that return type specified if return present
    def exit_return_stmt(self, node: ast.ReturnStmt) -> None:
        """Sub objects.

        expr: Optional[ExprType],
        """
        if node.expr:
            self.emit_ln(node, f"return {node.expr.meta['py_code']}")
        else:
            self.emit_ln(node, "return")

    def exit_yield_stmt(self, node: ast.YieldStmt) -> None:
        """Sub objects.

        expr: Optional[ExprType],
        """
        if node.expr:
            self.emit_ln(node, f"yield {node.expr.meta['py_code']}")
        else:
            self.emit_ln(node, "yield")

    @Pass.incomplete
    def exit_ignore_stmt(self, node: ast.IgnoreStmt) -> None:
        """Sub objects.

        target: ExprType,
        """
        self.ds_feature_warn()

    @Pass.incomplete
    def exit_visit_stmt(self, node: ast.VisitStmt) -> None:
        """Sub objects.

        typ: Optional[Token],
        target: Optional[ExprType],
        else_body: Optional[ElseStmt],
        """
        self.ds_feature_warn()

    @Pass.incomplete
    def exit_revisit_stmt(self, node: ast.RevisitStmt) -> None:
        """Sub objects.

        hops: Optional[ExprType],
        else_body: Optional[ElseStmt],
        """
        self.ds_feature_warn()

    @Pass.incomplete
    def exit_disengage_stmt(self, node: ast.DisengageStmt) -> None:
        """Sub objects."""
        self.ds_feature_warn()

    @Pass.incomplete
    def exit_sync_stmt(self, node: ast.SyncStmt) -> None:
        """Sub objects.

        target: ExprType,
        """
        self.ds_feature_warn()

    def exit_assignment(self, node: ast.Assignment) -> None:
        """Sub objects.

        is_static: bool,
        target: AtomType,
        value: ExprType,
        """

    def exit_binary_expr(self, node: ast.BinaryExpr) -> None:
        """Sub objects.

        left: ExprType,
        right: ExprType,
        op: Token,
        """

    def exit_if_else_expr(self, node: ast.IfElseExpr) -> None:
        """Sub objects.

        condition: BinaryExpr | IfElseExpr,
        value: ExprType,
        else_value: ExprType,
        """

    def exit_unary_expr(self, node: ast.UnaryExpr) -> None:
        """Sub objects.

        operand: ExprType,
        op: Token,
        """

    def exit_spawn_object_expr(self, node: ast.SpawnObjectExpr) -> None:
        """Sub objects.

        target: ExprType,
        """

    def exit_unpack_expr(self, node: ast.UnpackExpr) -> None:
        """Sub objects.

        target: ExprType,
        is_dict: bool,
        """

    def exit_multi_string(self, node: ast.MultiString) -> None:
        """Sub objects.

        strings: List[Token],
        """

    def exit_list_val(self, node: ast.ListVal) -> None:
        """Sub objects.

        values: List[ExprType],
        """

    def exit_expr_list(self, node: ast.ExprList) -> None:
        """Sub objects.

        values: List[ExprType],
        """

    def exit_dict_val(self, node: ast.DictVal) -> None:
        """Sub objects.

        kv_pairs: list,
        """

    def exit_comprehension(self, node: ast.Comprehension) -> None:
        """Sub objects.

        key_expr: Optional[ExprType],
        out_expr: ExprType,
        name: Token,
        collection: ExprType,
        conditional: Optional[ExprType],
        """

    def exit_k_v_pair(self, node: ast.KVPair) -> None:
        """Sub objects.

        key: ExprType,
        value: ExprType,
        """

    def exit_atom_trailer(self, node: ast.AtomTrailer) -> None:
        """Sub objects.

        target: AtomType,
        right: IndexSlice | ArchRefType | Token,
        null_ok: bool,
        """

    def exit_func_call(self, node: ast.FuncCall) -> None:
        """Sub objects.

        target: AtomType,
        params: Optional[ParamList],
        """

    def exit_param_list(self, node: ast.ParamList) -> None:
        """Sub objects.

        p_args: Optional[ExprList],
        p_kwargs: Optional[AssignmentList],
        """

    def exit_assignment_list(self, node: ast.AssignmentList) -> None:
        """Sub objects.

        values: List[ExprType],
        """

    def exit_index_slice(self, node: ast.IndexSlice) -> None:
        """Sub objects.

        start: ExprType,
        stop: Optional[ExprType],
        """

    def exit_global_ref(self, node: ast.GlobalRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_here_ref(self, node: ast.HereRef) -> None:
        """Sub objects.

        name: Optional[Token],
        """

    def exit_visitor_ref(self, node: ast.VisitorRef) -> None:
        """Sub objects.

        name: Optional[Token],
        """

    def exit_node_ref(self, node: ast.NodeRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_edge_ref(self, node: ast.EdgeRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_walker_ref(self, node: ast.WalkerRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_func_ref(self, node: ast.FuncRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_object_ref(self, node: ast.ObjectRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_ability_ref(self, node: ast.AbilityRef) -> None:
        """Sub objects.

        name: Token,
        """

    def exit_edge_op_ref(self, node: ast.EdgeOpRef) -> None:
        """Sub objects.

        filter_cond: Optional[ExprType],
        edge_dir: EdgeDir,
        """

    def exit_disconnect_op(self, node: ast.DisconnectOp) -> None:
        """Sub objects.

        filter_cond: Optional[ExprType],
        edge_dir: EdgeDir,
        """

    def exit_connect_op(self, node: ast.ConnectOp) -> None:
        """Sub objects.

        spawn: Optional[ExprType],
        edge_dir: EdgeDir,
        """

    def exit_spawn_ctx(self, node: ast.SpawnCtx) -> None:
        """Sub objects.

        spawns: List[Assignment],
        """

    def exit_filter_ctx(self, node: ast.FilterCtx) -> None:
        """Sub objects.

        compares: List[BinaryExpr],
        """
