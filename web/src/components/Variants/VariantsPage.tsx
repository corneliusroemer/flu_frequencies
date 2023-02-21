import React, { Suspense } from 'react'
import { Col, Container, Row } from 'reactstrap'
import { useRecoilValue } from 'recoil'
import { PageHeading } from 'src/components/Common/PageHeading'
import { VariantsPlot } from 'src/components/Variants/VariantsPlot'
import { VariantsSidebar } from 'src/components/Variants/VariantsSidebar'
import { PageContainerHorizontal, PageMainWrapper } from 'src/components/Layout/PageContainer'
import { pathogenAtom } from 'src/state/pathogen.state'
import { useTranslationSafe } from 'src/helpers/useTranslationSafe'
import { LOADING } from 'src/components/Loading/Loading'
import { useVariantsDataQuery } from 'src/io/getData'

export function VariantsPage() {
  const { t } = useTranslationSafe()
  const pathogen = useRecoilValue(pathogenAtom)
  const { variants } = useVariantsDataQuery(pathogen.name)

  return (
    <Suspense fallback={LOADING}>
      <PageContainerHorizontal>
        <VariantsSidebar />

        <PageMainWrapper>
          <Row noGutters>
            <Col>
              <PageHeading>{t('{{name}}: variants', { name: t(pathogen.nameFriendly) })}</PageHeading>
            </Col>
          </Row>
          <Row noGutters>
            <Col>
              <Container fluid>
                {variants.map((variant) => (
                  <Row key={variant} noGutters className="mb-5">
                    <Col>
                      <h3 className="text-center">{variant}</h3>
                      <VariantsPlot variantName={variant} />
                    </Col>
                  </Row>
                ))}
              </Container>
            </Col>
          </Row>
        </PageMainWrapper>
      </PageContainerHorizontal>
    </Suspense>
  )
}