# -*- coding: utf-8 -*-
"""Implements basics of Capa, including class CapaModule."""
import json
import logging
import re
import sys

from lxml import etree
from pkg_resources import resource_string

import dogstats_wrapper as dog_stats_api
from capa import responsetypes
from xmodule.exceptions import NotFoundError, ProcessingError
from xmodule.raw_module import RawDescriptor
from xmodule.util.misc import escape_html_characters
from xmodule.x_module import DEPRECATION_VSCOMPAT_EVENT, XModule, module_attr

from .capa_base import CapaFields, CapaMixin, ComplexEncoder

log = logging.getLogger("edx.courseware")


class CapaModule(CapaMixin, XModule):
    """
    An XModule implementing LonCapa format problems, implemented by way of
    capa.capa_problem.LoncapaProblem

    CapaModule.__init__ takes the same arguments as xmodule.x_module:XModule.__init__
    """
    icon_class = 'problem'

    js = {
        'js': [
            resource_string(__name__, 'js/src/javascript_loader.js'),
            resource_string(__name__, 'js/src/capa/display.js'),
            resource_string(__name__, 'js/src/collapsible.js'),
            resource_string(__name__, 'js/src/capa/imageinput.js'),
            resource_string(__name__, 'js/src/capa/schematic.js'),
        ]
    }

    js_module_name = "Problem"
    css = {'scss': [resource_string(__name__, 'css/capa/display.scss')]}

    def author_view(self, context):
        """
        Renders the Studio preview view.
        """
        return self.student_view(context)

    def handle_ajax(self, dispatch, data):
        """
        This is called by courseware.module_render, to handle an AJAX call.

        `data` is request.POST.

        Returns a json dictionary:
        { 'progress_changed' : True/False,
          'progress' : 'none'/'in_progress'/'done',
          <other request-specific values here > }
        """
        handlers = {
            'hint_button': self.hint_button,
            'problem_get': self.get_problem,
            'problem_check': self.submit_problem,
            'problem_reset': self.reset_problem,
            'problem_save': self.save_problem,
            'problem_show': self.get_answer,
            'score_update': self.update_score,
            'input_ajax': self.handle_input_ajax,
            'ungraded_response': self.handle_ungraded_response
        }

        _ = self.runtime.service(self, "i18n").ugettext

        generic_error_message = _(
            "We're sorry, there was an error with processing your request. "
            "Please try reloading your page and trying again."
        )

        not_found_error_message = _(
            "The state of this problem has changed since you loaded this page. "
            "Please refresh your page."
        )

        if dispatch not in handlers:
            return 'Error: {} is not a known capa action'.format(dispatch)

        before = self.get_progress()
        before_attempts = self.attempts

        try:
            result = handlers[dispatch](data)

        except NotFoundError:
            log.info(
                "Unable to find data when dispatching %s to %s for user %s",
                dispatch,
                self.scope_ids.usage_id,
                self.scope_ids.user_id
            )
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError(not_found_error_message), None, traceback_obj

        except Exception:
            log.exception(
                "Unknown error when dispatching %s to %s for user %s",
                dispatch,
                self.scope_ids.usage_id,
                self.scope_ids.user_id
            )
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError(generic_error_message), None, traceback_obj

        after = self.get_progress()
        after_attempts = self.attempts
        progress_changed = (after != before) or (after_attempts != before_attempts)
        curr_score, total_possible = self.get_display_progress()

        result.update({
            'progress_changed': progress_changed,
            'current_score': curr_score,
            'total_possible': total_possible,
            'attempts_used': after_attempts,
        })

        return json.dumps(result, cls=ComplexEncoder)

    @property
    def display_name_with_default(self):
        """
        Constructs the display name for a CAPA problem.

        Default to the display_name if it isn't None or not an empty string,
        else fall back to problem category.
        """
        if self.display_name is None or not self.display_name.strip():
            return self.location.block_type

        return self.display_name


class CapaDescriptor(CapaFields, RawDescriptor):
    """
    Module implementing problems in the LON-CAPA format,
    as implemented by capa.capa_problem
    """
    INDEX_CONTENT_TYPE = 'CAPA'

    module_class = CapaModule
    resources_dir = None

    has_score = True
    show_in_read_only_mode = True
    template_dir_name = 'problem'
    mako_template = "widgets/problem-edit.html"
    js = {'js': [resource_string(__name__, 'js/src/problem/edit.js')]}
    js_module_name = "MarkdownEditingDescriptor"
    has_author_view = True
    css = {
        'scss': [
            resource_string(__name__, 'css/editor/edit.scss'),
            resource_string(__name__, 'css/problem/edit.scss')
        ]
    }

    # The capa format specifies that what we call max_attempts in the code
    # is the attribute `attempts`. This will do that conversion
    metadata_translations = dict(RawDescriptor.metadata_translations)
    metadata_translations['attempts'] = 'max_attempts'

    @classmethod
    def filter_templates(cls, template, course):
        """
        Filter template that contains 'latex' from templates.

        Show them only if use_latex_compiler is set to True in
        course settings.
        """
        return 'latex' not in template['template_id'] or course.use_latex_compiler

    def get_context(self):
        _context = RawDescriptor.get_context(self)
        _context.update({
            'markdown': self.markdown,
            'enable_markdown': self.markdown is not None,
            'enable_latex_compiler': self.use_latex_compiler,
        })
        return _context

    # VS[compat]
    # TODO (cpennington): Delete this method once all fall 2012 course are being
    # edited in the cms
    @classmethod
    def backcompat_paths(cls, path):
        dog_stats_api.increment(
            DEPRECATION_VSCOMPAT_EVENT,
            tags=["location:capa_descriptor_backcompat_paths"]
        )
        return [
            'problems/' + path[8:],
            path[8:],
        ]

    @property
    def non_editable_metadata_fields(self):
        non_editable_fields = super(CapaDescriptor, self).non_editable_metadata_fields
        non_editable_fields.extend([
            CapaDescriptor.due,
            CapaDescriptor.graceperiod,
            CapaDescriptor.force_save_button,
            CapaDescriptor.markdown,
            CapaDescriptor.use_latex_compiler,
            CapaDescriptor.show_correctness,
        ])
        return non_editable_fields

    @property
    def problem_types(self):
        """ Low-level problem type introspection for content libraries filtering by problem type """
        try:
            tree = etree.XML(self.data)
        except etree.XMLSyntaxError:
            log.error('Error parsing problem types from xml for capa module {}'.format(self.display_name))
            return None  # short-term fix to prevent errors (TNL-5057). Will be more properly addressed in TNL-4525.
        registered_tags = responsetypes.registry.registered_tags()
        return {node.tag for node in tree.iter() if node.tag in registered_tags}

    def index_dictionary(self):
        """
        Return dictionary prepared with module content and type for indexing.
        """
        xblock_body = super(CapaDescriptor, self).index_dictionary()
        # Removing solutions and hints, as well as script and style
        capa_content = re.sub(
            re.compile(
                r"""
                    <solution>.*?</solution> |
                    <script>.*?</script> |
                    <style>.*?</style> |
                    <[a-z]*hint.*?>.*?</[a-z]*hint>
                """,
                re.DOTALL |
                re.VERBOSE),
            "",
            self.data
        )
        capa_content = escape_html_characters(capa_content)
        capa_body = {
            "capa_content": capa_content,
            "display_name": self.display_name,
        }
        if "content" in xblock_body:
            xblock_body["content"].update(capa_body)
        else:
            xblock_body["content"] = capa_body
        xblock_body["content_type"] = self.INDEX_CONTENT_TYPE
        xblock_body["problem_types"] = list(self.problem_types)
        return xblock_body

    def has_support(self, view, functionality):
        """
        Override the XBlock.has_support method to return appropriate
        value for the multi-device functionality.
        Returns whether the given view has support for the given functionality.
        """
        if functionality == "multi_device":
            types = self.problem_types  # Avoid calculating this property twice
            return types is not None and all(
                responsetypes.registry.get_class_for_tag(tag).multi_device_support
                for tag in types
            )
        return False

    def max_score(self):
        """
        Return the problem's max score
        """
        from capa.capa_problem import LoncapaProblem, LoncapaSystem
        capa_system = LoncapaSystem(
            ajax_url=None,
            anonymous_student_id=None,
            cache=None,
            can_execute_unsafe_code=None,
            get_python_lib_zip=None,
            DEBUG=None,
            filestore=self.runtime.resources_fs,
            i18n=self.runtime.service(self, "i18n"),
            node_path=None,
            render_template=None,
            seed=None,
            STATIC_URL=None,
            xqueue=None,
            matlab_api_key=None,
        )
        lcp = LoncapaProblem(
            problem_text=self.data,
            id=self.location.html_id(),
            capa_system=capa_system,
            capa_module=self,
            state={},
            seed=1,
            minimal_init=True,
        )
        return lcp.get_max_score()

    # FIXME delete course_key and block_key parameters (they are implicit)
    # FIXME delete get_block parameter (unneeded?)
    # FIXME implement filter by user_ids and match_string
    # v1:
    # def generate_report_data(self, course_key=None, block_key=None, get_block=None, user_ids=None, match_string=None):
    # v2 (static):
    # FIXME make static so that it can run in a smaller runtime, with ~~~~ only a CapaDescriptor, see e.g. CapaDescriptor.max_score about how to build such runtime. Maybe move to CapaDescriptor
    # @staticmethod
    # def generate_report_data(descriptor):
    # v3: non-static, and receive user_state_client as parameter
    def generate_report_data(self, user_state_iterator, limit_responses=None):
        """
        Return a list of student responses to this block in a readable way.

        Arguments:
            user_state_iterator: iterator over UserStateClient objects.
                E.g. the result of user_state_client.iter_all_for_block(block_key)

            limit_responses (int/None): maximum number of responses to include.
                Set to None (default) to include all.

        Returns:
            each call returns a tuple like:
            ("username", {"Question": "2 + 2 equals how many?", "Answer": "Four"})
        """

        # import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()

        if False and "testing with static":
            # import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()
            self = descriptor

            # from xmodule.tests import DATA_DIR, get_test_system, get_test_descriptor_system
            # self.xmodule_runtime = get_test_system()
            # assert self.xmodule_runtime

        if self.category != 'problem':
            raise NotImplementedError()
        # FIXME reimplement without using self.lcp (to make it work with the static one)
        if False and 'customresponse' in [elem.tag for elem in self.lcp.responder_answers.keys()]:
            raise NotImplementedError("Not implemented for custom response problems "
                                      "(like drag&drop, chemical equations etc.)")

        # FIXME remove these tests:
        # from opaque_keys.edx.keys import CourseKey, UsageKey
        # block_key = UsageKey.from_string('block-v1:edX+DemoX+Demo_Course+type@problem+block@a0effb954cca4759994f1ac9e9434bf4')

        block_key = self.location

        # FIXME needed?
        try:
            tree = etree.XML(self.data)
        except etree.XMLSyntaxError:
            log.error('Error parsing problem types from xml for capa module {}'.format(self.display_name))
            return


        from capa.capa_problem import LoncapaProblem, LoncapaSystem
        capa_system = LoncapaSystem(
            ajax_url=None,
            anonymous_student_id=None,
            cache=None,
            can_execute_unsafe_code=None,
            get_python_lib_zip=None,
            DEBUG=None,
            filestore=self.runtime.resources_fs,
            i18n=self.runtime.service(self, "i18n"),
            node_path=None,
            render_template=None,
            seed=1,
            STATIC_URL=None,
            xqueue=None,
            matlab_api_key=None,
        )

        # import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()

        # FIXME remove this step
        states = list(user_state_iterator)
        print("I am seeing the following user_state:", states)

        for idx, user_state in enumerate(states):

            if limit_responses and idx >= limit_responses:
                break

            if 'student_answers' not in user_state.state:
                continue

            print("This part is new. FIXME test it")

            #capa_system.anonymous_student_id = # FIXME re-set the anonymous ID to this student's anonymous ID somehow?
            lcp = LoncapaProblem(
                problem_text=self.data,
                id=self.location.html_id(),
                capa_system=capa_system,
                capa_module=self, # FIXME: self is a CapaDescriptor, not a CapaModule. Does this make sense? Without a CapaModule, we can't use functions like get_submission_metadata()
                state={
                    'done': user_state.state.get('done'),
                    'correct_map': user_state.state.get('correct_map'),
                    'student_answers': user_state.state.get('student_answers'),
                    'has_saved_answers': user_state.state.get('has_saved_answers'),
                    'input_state': user_state.state.get('input_state'),
                    'seed': user_state.state.get('seed'),
                },
                seed=user_state.state.get('seed'),
                # extract_tree=False allows us to work without a fully initialized CapaModule
                # We'll still be able to find particular data in the XML when we need it
                extract_tree=False,
            )

            def find_question_label_for_answer(question_id): # FIXME fix names.   FIXME: move function. # FIXME doc
                """
                Obtain the most relevant question text for a particular question.
                This is, in order:
                - the question prompt, if the question has one
                - the <p> or <label> element which precedes the choices (skipping descriptive elements)
                - a text like "Question 5" if no other name could be found
                """
                assert question_id in lcp.problem_data
                problem_data = lcp.problem_data[question_id]
                prompt = problem_data.get('label', problem_data.get('descriptions').values())  # FIXME rename
                if prompt:
                    question_text = prompt.striptags()
                else:

                    xml_elems = [elem for elem, data in lcp.responder_answers.iteritems() if question_id in data]
                    assert len(xml_elems) == 1, (len(xml_elems), xml_elems, question_id, list(lcp.responder_answers.iteritems()))

                    # Get the element that probably contains the question text
                    questiontext_elem = xml_elems[0].getprevious()

                    # Go backwards, skip <description> and other responses, because they don't contain the question
                    skip_elems = responsetypes.registry.registered_tags() + ['description']
                    while questiontext_elem is not None and questiontext_elem.tag in skip_elems:
                        questiontext_elem = questiontext_elem.getprevious()

                    if questiontext_elem is not None and questiontext_elem.tag in ['p', 'label']:
                        question_text = questiontext_elem.text
                    else:
                        # question_text = None
                        # For instance 'd2e35c1d294b4ba0b3b1048615605d2a_2_1' contains 2, which is used in question number 1
                        question_nr = int(question_id.split('_')[1])-1
                        question_text = "Question %i" % question_nr

                return question_text

            def find_answer_text(question_id, current_answer_text):  # FIXME fix names.   FIXME: move function. # FIXME doc
                # import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()

                # if question_id == '98e6a8e915904d5389821a94e48babcf_11_1':
                #     import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()

                if type(current_answer_text) == list:
                    # we need to join them
                    answer_text = ""
                    for choice_number in current_answer_text:
                        for element, response in lcp.responders.iteritems():
                            # print("Did I find it yet?", question_id, response.answer_ids)
                            # if response.answer_id == question_id:
                            if question_id in response.answer_ids:
                                if response.inputfields:

                                    # debug:
                                    # from lxml import etree; print(etree.tostring(response.inputfields[0], pretty_print=True))

                                    for choice_el in response.inputfields[0].getchildren():
                                        if choice_el.get('name') == choice_number:
                                            answer_text += choice_el.text + ", "
                                break
                    return answer_text
                else:
                    assert not current_answer_text.startswith('choice_')  # FIXME remove when it's for sure
                    # already a string with the answer
                    return current_answer_text

                
            for question_id, orig_answers in lcp.get_question_answers().items():
                if '_solution_' in question_id:
                    # FIXME I think this is not really a question/answer and can be skipped. But verify
                    continue
                elif question_id not in lcp.problem_data:
                    print("FIXME debug this case. Maybe it happened only with the _solution_ scenario")
                    print(question_id)
                    print(lcp.problem_data)
                    import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()


                question_text = find_question_label_for_answer(question_id)
                answer_text = find_answer_text(question_id, current_answer_text=orig_answers)

                # print(type(question_text), type(answer_text), question_id)
                print("On question {question_id} ({description}) user {username} answered «{answer}» (DEBUG: original answer: {orig_answers}".format(
                    question_id=question_id,
                    description=question_text.encode('utf-8'),
                    username=user_state.username,
                    answer=answer_text,
                    orig_answers=orig_answers
                ))
            return

            student_answers = user_state.state['student_answers']

            for question_id, answer in student_answers.iteritems():
                question_column = "see above code"


                answer_with_names = "FIXME: redo this part to get the answer, so that it can get the right answers with the static function"
                # import sys; sys.stdout = sys.__stdout__; import ipdb; ipdb.set_trace()
                if True and "disabled when using static":
                    metad = self.get_submission_metadata({question_id: answer}, self.lcp.correct_map)

                    assert question_id in metad
                    answer_with_names = metad[question_id]['answer']
                    if type(answer_with_names) == list:
                        answer_with_names = ",".join(answer_with_names)
                answer_column = answer_with_names

                # FIXME delete this (original answer)
                # answer_column = "".join(answer)

                xml_string = etree.tostring(tree, pretty_print=True)
                xml_string = xml_string.replace("<", "&lt;")
                xml_string = xml_string.replace(">", "&gt;")
                xml_string = xml_string.replace("\n", "<br />")
                # print(xml_string)
                yield (user_state.username, {
                    "Question": question_column, "Answer": answer_column,
                    # "BTW metadata": metad,
                    # "BTW here's the XML which contains the question too": xml_string,
                })


    # Proxy to CapaModule for access to any of its attributes
    answer_available = module_attr('answer_available')
    submit_button_name = module_attr('submit_button_name')
    submit_button_submitting_name = module_attr('submit_button_submitting_name')
    submit_problem = module_attr('submit_problem')
    choose_new_seed = module_attr('choose_new_seed')
    closed = module_attr('closed')
    # generate_report_data = module_attr('generate_report_data')
    find_question_label_for_answer = module_attr('find_question_label_for_answer')
    get_answer = module_attr('get_answer')
    get_problem = module_attr('get_problem')
    get_problem_html = module_attr('get_problem_html')
    get_state_for_lcp = module_attr('get_state_for_lcp')
    handle_input_ajax = module_attr('handle_input_ajax')
    hint_button = module_attr('hint_button')
    handle_problem_html_error = module_attr('handle_problem_html_error')
    handle_ungraded_response = module_attr('handle_ungraded_response')
    has_submitted_answer = module_attr('has_submitted_answer')
    is_attempted = module_attr('is_attempted')
    is_correct = module_attr('is_correct')
    # correctness_available = module_attr('correctness_available')     # FIXME remove
    is_past_due = module_attr('is_past_due')
    is_submitted = module_attr('is_submitted')
    lcp = module_attr('lcp')
    make_dict_of_responses = module_attr('make_dict_of_responses')
    new_lcp = module_attr('new_lcp')
    publish_grade = module_attr('publish_grade')
    rescore = module_attr('rescore')
    reset_problem = module_attr('reset_problem')
    save_problem = module_attr('save_problem')
    set_score = module_attr('set_score')
    set_state_from_lcp = module_attr('set_state_from_lcp')
    should_show_submit_button = module_attr('should_show_submit_button')
    should_show_reset_button = module_attr('should_show_reset_button')
    should_show_save_button = module_attr('should_show_save_button')
    update_score = module_attr('update_score')
